# -*- coding: utf-8 -*-
from odoo.tools.safe_eval import safe_eval
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, ustr
from odoo.osv.expression import OR, normalize_domain

from datetime import datetime
import re
import ast


PROTECTED_KEYWORDS = (
    'sum', 'sum_if_pos', 'sum_if_neg',
    'sum_if_pos_groupby', 'sum_if_neg_groupby',
    'debit', 'credit', 'balance',
    'count_rows', 'from_context', 'NDays',
    '__builtins__'
)


class FormulaLocals(dict):
    ''' Class to set as "locals" when evaluating the formula to compute all formula.
    The evaluation must be done for each key so this class takes a key as parameter.
    '''

    def __init__(self, solver, financial_line, key):
        super().__init__()
        self.solver = solver
        self.financial_line = financial_line
        self.key = key

    def __getitem__(self, item):
        if item == 'NDays':
            return self.solver._get_number_of_days(self.key[0])
        elif item == 'from_context':
            return self.solver._get_balance_from_context(self.financial_line)
        elif item == 'count_rows':
            return self.solver._get_amls_results(self.financial_line, item)[item].get(self.key[0], 0)
        elif item in ('sum', 'sum_if_pos', 'sum_if_neg', 'sum_if_pos_groupby', 'sum_if_neg_groupby'):
            return self.solver._get_amls_results(self.financial_line, item)[item].get(self.key, 0.0)
        else:
            financial_line = self.solver._get_line_by_code(item)
            if not financial_line:
                return super().__getitem__(item)
            return self.solver._get_formula_results(financial_line).get(self.key, 0.0)


class FormulaSolver:
    def __init__(self, options_list, financial_report):
        self.options_list = options_list
        self.financial_report = financial_report
        self.env = financial_report.env      
        self.cache_line_by_code = {}
        self.cache_results_by_id = {}
        self.encountered_keys = set()

    # -------------------------------------------------------------------------
    # PRIVATE METHODS
    # -------------------------------------------------------------------------

    def _eval_formula(self, expression_formula, key, financial_line):
        ''' Evaluate the current formula using the custom object passed as a parameter as locals.
        :param expression_formula: The formula string from the related expression record.
        :param key:                A tuple being the concatenation of the period index plus the additional group-by keys.
                                   Suppose you are evaluating the formula for 'partner_id'=3 for the first comparison, the
                                   key will be (1, 3).
        :param financial_line:     A record of the account.report.line model.
        '''
        if not expression_formula:
            return 0.0
        
        try:
            return safe_eval(expression_formula, globals_dict=FormulaLocals(self, financial_line, key), nocopy=True)
        except ZeroDivisionError:
            return 0.0


    def _get_line_by_code(self, line_code):
        ''' Retrieve an account.financial.html.report.line record from its code.
        If the financial line is not already known, a search is made and its formula is directly evaluated to collect
        all involved keys by this newly added line.
        :param line_code:   The code that could be owned by the account.financial.html.report.line record.
        :return:            An account.financial.html.report.line recordset having 0 or 1 as arity.
        '''
        if line_code in self.cache_line_by_code:
            # Line is already cached.
            return self.cache_line_by_code[line_code]
        else:
            # Fetch line.
            financial_line = self.env['account.report.line'].search([('code', '=', line_code)], limit=1)

            if financial_line:
                self._prefetch_line(financial_line)

            return financial_line

    def _get_formula_results(self, financial_line):
        ''' Get or compute the 'formula' results of a financial report line (see 'cache_results_by_id').
        :param financial_line:  A record of the account.report.line model.
        :return: see 'cache_results_by_id', 'formula' key.
        '''
        self.cache_results_by_id.setdefault(financial_line.id, {})
    
        if 'formula' not in self.cache_results_by_id[financial_line.id]:
            results = {}
            # Retrieve the related expression from AccountReportExpression
            expression = self.env['account.report.expression'].search([('report_line_id', '=', financial_line.id)])     
            if expression and expression.formula:
                for key in self.encountered_keys:
                    # Compute formula for each key.
                    results[key] = self._eval_formula(expression.formula, key, financial_line) 
    
            self.cache_results_by_id[financial_line.id]['formula'] = results
    
        return self.cache_results_by_id[financial_line.id]['formula']
    
    def _get_subformula_results(self, financial_line):
        ''' Get or compute the 'formula' results of a financial report line (see 'cache_results_by_id').
        :param financial_line:  A record of the account.report.line model.
        :return: see 'cache_results_by_id', 'formula' key.
        '''      
        expression = self.env['account.report.expression'].search([('report_line_id', '=', financial_line.id)])            
        subformula = ''
        if expression and expression.subformula:
            subformula = expression.subformula  
        return subformula

    def _get_amls_results(self, financial_line, operator):
        ''' Get or compute the 'amls' results of a financial report line (see 'cache_results_by_id').
        :param financial_line:  A record of the account.report.line model.
        :return: see 'cache_results_by_id', 'amls' key.
        '''
        self.cache_results_by_id.setdefault(financial_line.id, {})

        if 'amls' not in self.cache_results_by_id[financial_line.id]:            
            expression = self.env['account.report.expression'].search([('report_line_id', '=', financial_line.id)])             
            if expression:             
                results = financial_line._compute_sum(self.options_list, self.financial_report)
                for key in results['sum']:
                    self.encountered_keys.add(key)
                if expression.engine == 'domain' and re.search(r'-\s*sum', expression.formula):
                    results['sign'] = -1
                else:
                    results['sign'] = 1
                results['operator'] = operator
                self.cache_results_by_id[financial_line.id]['amls'] = results
        return self.cache_results_by_id[financial_line.id]['amls']
    
    def _prefetch_line(self, financial_line):
        ''' Ensure all leaves that depends of this line are evaluated.
        E.g. if the formula is 'A + B', make sure 'A' and 'B' are also fetch.
        If 'A' is a leaf, its formula will be evaluated directly.
        :param financial_line:  A record of the account.financial.html.report.line model.
        '''     
        if financial_line.code:
            self.cache_line_by_code[financial_line.code] = financial_line
        self.cache_results_by_id.setdefault(financial_line.id, {})
        if not financial_line.formulas:
            return
        
        class LeafResolver(ast.NodeTransformer):    
            def __init__(self, solver, financial_line):
                self.solver = solver
                self.financial_line = financial_line
            def visit_Name(self, node):
                if node.id in ('sum', 'sum_if_pos', 'sum_if_neg', 'sum_if_pos_groupby', 'sum_if_neg_groupby'):                 
                    self.solver._get_amls_results(self.financial_line, node.id)
                else:                
                    financial_line = self.solver._get_line_by_code(node.id)
                    if financial_line:
                        self.solver.cache_results_by_id[self.financial_line.id].setdefault('sub_codes', set())
                        self.solver.cache_results_by_id[self.financial_line.id]['sub_codes'].add(financial_line.code)

                return node
        LeafResolver(self, financial_line).visit(ast.parse(financial_line.formulas))

    def _get_number_of_days(self, period_index):
        ''' Helper to compute the NDays value that could be used inside formulas. This key returns the number of days
        inside the current period.
        :param period_index:    The period number, 0 being the current one.
        :return:                The number of days inside the period.
        '''
        options = self.options_list[period_index]
        date_from = datetime.strptime(options['date']['date_from'], DEFAULT_SERVER_DATE_FORMAT).date()
        date_to = datetime.strptime(options['date']['date_to'], DEFAULT_SERVER_DATE_FORMAT).date()
        return (date_to - date_from).days

    def _get_balance_from_context(self, financial_line):
        ''' Retrieve the balance from context.
        :param financial_line:  A record of the account.financial.html.report.line model.
        :return:                The balance found in the context or 0.0.
        '''
        financial_report_line_values = self.options_list[0].get('financial_report_line_values', {})
        return financial_report_line_values.get(financial_line.code, 0.0)

    # -------------------------------------------------------------------------
    # PUBLIC METHODS
    # -------------------------------------------------------------------------

    def get_results(self, financial_line):
        ''' Get results for the given financial report line.
        :param financial_line:  A record of the account.financial.html.report.line model.
        :return: see 'cache_results_by_id' for more details.
        '''
        if financial_line.id not in self.cache_results_by_id:  
            return {}
        self._get_formula_results(financial_line)

        return self.cache_results_by_id[financial_line.id]

    def fetch_lines(self, financial_lines):
        ''' Prefetch lines passed as parameter.
        The lines involved through a formula will also be prefetched.
        :param financial_lines: An account.financial.html.report.line recordset.
        '''
        children_financial_lines = self.env['account.report.line']
        for financial_line in financial_lines:
            self._prefetch_line(financial_line)
            children_financial_lines += financial_line.children_ids
        if children_financial_lines:
            self.fetch_lines(children_financial_lines)

    def get_keys(self):
        ''' Get all involved keys found in the solver. '''
        return self.encountered_keys

    def is_leaf(self, financial_line):
        ''' Helper telling if the financial line passed as parameter is a leaf. '''
        return 'amls' in self.cache_results_by_id.get(financial_line.id, {})

    def has_move_lines(self, financial_line):
        ''' Helper telling if the financial line passed as parameter has some move lines in its domain. '''
        if not self.is_leaf(financial_line):
            return False
        total_count_rows = sum(self.cache_results_by_id[financial_line.id]['amls']['count_rows'].values())
        return bool(total_count_rows)

    def get_formula_string(self, financial_line):
        ''' Helper to get a formula with replaced amounts. '''

        def inject_in_formula(formula, to_replace, to_write, is_monetary=False):    
            if to_replace == 'sum' and is_monetary and to_write < 0.0 and re.sub(r'\s*', '', formula) == '-sum':
                return self.env['account.report'].format_value(-to_write)

            if is_monetary:
                to_write = self.env['account.report'].format_value(to_write)
            return re.sub(r'(?<!\w)%s(?=(\W|$))' % to_replace, str(to_write), formula)
        formula = financial_line.formulas
        if not formula:
            return ''

        results = self.get_results(financial_line)

        if self.is_leaf(financial_line):  
            formula = inject_in_formula(formula, 'count_rows', results['amls']['count_rows'].get(0, 0))

            # Manage 'sum', 'sum_if_pos', 'sum_if_neg'.
            for keyword in ('sum', 'sum_if_pos', 'sum_if_neg', 'sum_if_pos_groupby', 'sum_if_neg_groupby'):
                balance = sum(results['amls'][keyword].values())
                formula = inject_in_formula(formula, keyword, balance, is_monetary=True)

        # Manage 'from_context': Display context value inside the first options.
        formula = inject_in_formula(formula, 'from_context', self._get_balance_from_context(financial_line), is_monetary=True)

        # Manage 'NDays': Display only the NDays for the current period.
        formula = inject_in_formula(formula, 'NDays', self._get_number_of_days(0))

        # Manage involved sub-formula.
        for code in results.get('sub_codes', []):
            other_line = self.cache_line_by_code[code]

            # A financial line could have no code since the field is not required.
            if not other_line.code:
                continue

            formula_results = self._get_formula_results(other_line)
            balance = sum(formula_results.values())
            formula = inject_in_formula(formula, other_line.code, balance, is_monetary=True)

        return formula

    def get_formula_popup(self, financial_line):
        """ Helper to enrich the formula with relevant cross-linking metadata.

        Each cross-linkable code in the formula of ``financial_line`` gets
        converted to a node ``{type: internal, code: ...}`` if it comes from a
        line from the same report as ``financial_line``, or
        ``{type: external, id: current_report_id, target: report_id, code: ...}``
        otherwise.

        Content which is not cross-linkable is converted to
        ``{type: literal, text: ...}``, this includes both non-code contents and
        codes which could not be resolved.
        """
        results = self.get_results(financial_line)

        formula = financial_line.formulas

        if not formula:
            return []

        codes = results.get('sub_codes')
        if not codes:
            return [formula]

        items = []
        prev = 0
        for m in re.finditer(r'\b' + '|'.join(codes) + r'\b', formula):
            code = m[0]
            # line might have no code as the field is optional
            other_line = self.cache_line_by_code[code]
            if not other_line.code:
                continue

            if m.start() != prev:
                items.append({'type': 'literal', 'text': formula[prev:m.start()]})
            prev = m.end()

            financial_report = other_line._get_financial_report()
            if not financial_report or financial_report == self.financial_report:
                items.append({
                    'type': 'internal',
                    'code': other_line.code,
                })
            else:
                items.append({
                    'type': 'external',
                    'id': self.financial_report.id,
                    'target': financial_report.id,
                    'code': other_line.code,
                })

        rest = formula[prev:]
        if rest:
            items.append(rest)

        return items

    def _get_involved_sub_financial_line_domains(self, financial_line):
        """ Recursively goes through each line's sub lines in order to find their respective domain.
        :return:    A list of domains.
        """

        results = self.get_results(financial_line)
        if 'involved_sub_financial_line_domains' not in results:
            sub_codes = results.get('sub_codes', [])
            involved_sub_financial_line_domains = []
            if not sub_codes:
                line_domain = ast.literal_eval(ustr(financial_line.domain))
                involved_sub_financial_line_domains.append(line_domain)
            for sub_code in sub_codes:
                sub_line = self.cache_line_by_code[sub_code]
                for line_id in self._get_involved_sub_financial_line_domains(sub_line):
                    involved_sub_financial_line_domains.append(line_id)
            results['involved_sub_financial_line_domains'] = involved_sub_financial_line_domains
        return results['involved_sub_financial_line_domains']

    def _has_missing_control_domain(self, options, financial_line):
        return bool(self._get_missing_control_domain(options, financial_line))

    def _has_excess_control_domain(self, options, financial_line):
        return bool(self._get_excess_control_domain(options, financial_line))

    def _get_missing_control_domain(self, options, financial_line):
        """ Compares the control domain with all the domains involved in the sub lines.
        :return:   The domain containing the missing items.
        """

        involved_domains = self._get_involved_sub_financial_line_domains(financial_line)
        control_domain = ast.literal_eval(ustr(financial_line.control_domain))

        comparison_domain = OR(involved_domains)
        missing_domain = control_domain + ['!'] + normalize_domain(comparison_domain)
        has_missing = bool(self.env['account.move.line'].search(missing_domain, limit=1))

        return missing_domain if has_missing else []

    def _get_excess_control_domain(self, options, financial_line):
        """ Compares each of the involved domains with the difference between:
                A- The control domain
                B- All the remaining domains
        In order to find potential duplicate journal items.
        :return:   The domain containing the excess items.
        """

        involved_domains = self._get_involved_sub_financial_line_domains(financial_line)
        control_domain = ast.literal_eval(ustr(financial_line.control_domain))

        excess_domains = []
        for i, domain in enumerate(involved_domains):
            remaining_domains = OR(involved_domains[:i] + involved_domains[i+1:])
            comparison_domain = control_domain + ['!'] + normalize_domain(remaining_domains)

            excess_domain = domain + ['!'] + normalize_domain(comparison_domain)
            has_excess = bool(self.env['account.move.line'].search(excess_domain, limit=1))
            if has_excess:
                excess_domains.append(excess_domain)

        return OR(excess_domains) if excess_domains else []