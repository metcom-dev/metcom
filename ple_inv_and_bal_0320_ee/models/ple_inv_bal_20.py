from odoo import fields, models, api, _
from markupsafe import Markup
from odoo.tools import config,ustr
import ast


class AccountReportLineInherit(models.Model):
    _inherit = 'account.report.line'

    re_item = fields.Many2one('eeff.ple', string='3.20 Rubro ER')
    
    date_scope = fields.Selection(
    related='expression_ids.date_scope',
    string='Date Scope',
    store=False,  # No almacena el valor en la base de datos, ya que es solo de lectura
    )            

    def _get_domain(self, options, financial_report):
        ''' Get the domain to be applied on the current line.
        :return: A valid domain to apply on the account.move.line model.
        '''
        self.ensure_one()

        # Domain defined on the line.
        domain = self.domain_formula and ast.literal_eval(ustr(self.domain_formula)) or []

        # Take care of the tax exigibility.
        # /!\ Still needed as there are still some custom tax reports in localizations.
        if financial_report.tax_report:
            domain += self.env['account.move.line']._get_tax_exigible_domain()

        return domain
    def _get_financial_report(self):
        ''' Retrieve the financial report owning the current line.
        The current financial report you are rendering is not always the report owning the
        lines as you could reference a line in a formula coming from another report.

        :return: An account.report record.
        '''
        self.ensure_one()
        line = self
        financial_report = False
        while not financial_report:
            financial_report = line.report_id
            if not line.parent_id:
                break
            line = line.parent_id
        return financial_report

    def _get_options_financial_line(self, options, calling_financial_report, parent_financial_report):
        ''' Create a new options specific to one financial line.
        :param options:                     The report options.
        :param calling_financial_report:    The financial report called by the user to be rendered.
        :param parent_financial_report:     The financial report owning the current financial report line that need to
                                            be evaluated by the solver.
        :return:                            The report options adapted to the financial line.
        '''
        self.ensure_one()
    
        # Verificar si la clave 'date' está presente en options
        if 'date' in options:
            # Asegurarse de que 'date' sea un diccionario
            if not isinstance(options['date'], dict):
                raise ValueError("La clave 'date' en options debe ser un diccionario.")
        else:
            # Si 'date' no está presente en options, puedes manejarlo de acuerdo a tus necesidades.
            # Aquí se establece un valor predeterminado.
            options['date'] = {'date_from': False, 'date_to': False, 'filter': 'custom'}
    
        new_options = options.copy()
        new_options['date'] = options['date'].copy()
        new_options['date'].update({'mode': 'range'})
        date_from = options['date']['date_from']
        date_to = options['date']['date_to']
        if self.date_scope == 'strict_range':
            new_options['date']['strict_range'] = True
        elif self.date_scope == 'from_beginning':
            new_options['date']['date_from'] = False
        elif self.date_scope == 'to_beginning_of_period':
            date_tmp = fields.Date.from_string(date_from) - relativedelta(days=1)
            date_to = date_tmp.strftime('%Y-%m-%d')
            new_options['date'].update({'date_from': False, 'date_to': date_to, 'strict_range': False})
        elif self.date_scope == 'from_fiscalyear':
            date_tmp = fields.Date.from_string(date_to)
            date_tmp = self.env.company.compute_fiscalyear_dates(date_tmp)['date_from']
            date_from = date_tmp.strftime('%Y-%m-%d')
            new_options['date'].update({'date_from': date_from, 'date_to': date_to, 'strict_range': True, 'mode': 'range'})
        elif self.date_scope == 'to_beginning_of_fiscalyear':
            date_tmp = fields.Date.from_string(date_to)
            date_tmp = self.env.company.compute_fiscalyear_dates(date_tmp)['date_from'] - relativedelta(days=1)
            date_to = date_tmp.strftime('%Y-%m-%d')
            new_options['date'].update({'date_from': False, 'date_to': date_to, 'strict_range': True, 'mode': 'range'})
        return new_options

    
    def _compute_sum(self, options_list, calling_financial_report):
        ''' Compute the values to be used inside the formula for the current line.
        If called, it means the current line formula contains something making its line a leaf ('sum' or 'count_rows')
        for example.

        The results is something like:
        {
            'sum':                  {key: <balance>...},
            'sum_if_pos':           {key: <balance>...},
            'sum_if_pos_groupby':   {key: <balance>...},
            'sum_if_neg':           {key: <balance>...},
            'sum_if_neg_groupby':   {key: <balance>...},
            'count_rows':           {period_index: <number_of_rows_in_period>...},
        }

        ... where:
        'period_index' is the number of the period, 0 being the current one, others being comparisons.

        'key' is a composite key containing the period_index and the additional group by enabled on the financial report.
        For example, suppose a group by 'partner_id':

        The keys could be something like (0,1), (1,2), (1,3), meaning:
        * (0,1): At the period 0, the results for 'partner_id = 1' are...
        * (1,2): At the period 1 (first comparison), the results for 'partner_id = 2' are...
        * (1,3): At the period 1 (first comparison), the results for 'partner_id = 3' are...

        :param options_list:                The report options list, first one being the current dates range, others
                                            being the comparisons.
        :param calling_financial_report:    The financial report called by the user to be rendered.
        :return:                            A python dictionary.
        '''
        self.ensure_one()
        params = []
        queries = []

        AccountFinancialReportHtml = self.report_id
        groupby_list = AccountFinancialReportHtml._get_options_groupby_fields(options_list[0])
        all_groupby_list = groupby_list.copy()
        
        # Obtén las fórmulas de la expresión relacionada
        formulas = self.expression_ids.formula if self.expression_ids else ''
        
        groupby_in_formula = any(x in formulas for x in ('sum_if_pos_groupby', 'sum_if_neg_groupby'))
        
        if groupby_in_formula and self.groupby and self.groupby not in all_groupby_list:
            all_groupby_list.append(self.groupby)
        
        groupby_clause = ','.join('account_move_line.%s' % gb for gb in all_groupby_list)

        parent_financial_report = self._get_financial_report()


        # Prepare a query by period as the date is different for each comparison.

        for i, options in enumerate(options_list):
            new_options = self._get_options_financial_line(options, calling_financial_report, parent_financial_report)          
            line_domain = self._get_domain(new_options, parent_financial_report)

            ct_query = self.env['res.currency']._get_query_currency_table(options)
            tables, where_clause, where_params = AccountFinancialReportHtml._query_get(new_options, self.date_scope,  domain=line_domain)

            queries.append('''
                SELECT
                    ''' + (groupby_clause and '%s,' % groupby_clause) + ''' %s AS period_index,
                    COUNT(DISTINCT account_move_line.''' + (self.groupby or 'id') + ''') AS count_rows,
                    COALESCE(SUM(ROUND(account_move_line.balance * currency_table.rate, currency_table.precision)), 0.0) AS balance
                FROM ''' + tables + '''
                JOIN ''' + ct_query + ''' ON currency_table.company_id = account_move_line.company_id
                WHERE ''' + where_clause + '''
                ''' + (groupby_clause and 'GROUP BY %s' % groupby_clause) + '''
            ''')
            params.append(i)
            params += where_params

        # Fetch the results.

        results = {
            'sum': {},
            'sum_if_pos': {},
            'sum_if_pos_groupby': {},
            'sum_if_neg': {},
            'sum_if_neg_groupby': {},
            'count_rows': {},
        }

        self._cr.execute(' UNION ALL '.join(queries), params)
        for res in self._cr.dictfetchall():
            # Build the key.
            key = [res['period_index']]
            for gb in groupby_list:
                key.append(res[gb])
            key = tuple(key)

            # Compute values.
            results['count_rows'].setdefault(res['period_index'], 0)
            results['count_rows'][res['period_index']] += res['count_rows']
            results['sum'][key] = res['balance']
            if results['sum'][key] > 0:
                results['sum_if_pos'][key] = results['sum'][key]
                results['sum_if_pos_groupby'].setdefault(key, 0.0)
                results['sum_if_pos_groupby'][key] += res['balance']
            if results['sum'][key] < 0:
                results['sum_if_neg'][key] = results['sum'][key]
                results['sum_if_neg_groupby'].setdefault(key, 0.0)
                results['sum_if_neg_groupby'][key] += res['balance']

        return results



class ReportAccountReportInherit(models.Model):
    _inherit = "account.report"

    tax_report = fields.Boolean('Tax Report', help="Set to True to automatically filter out journal items that are not tax exigible.")
    allow_txt_generation = fields.Selection(
        [('20', '3.20 Estado de resultados')],
        string='Permitir la generación del txt'
    )
    company_id = fields.Many2one(
        comodel_name='res.company',
        required=True,
        default=lambda self: self.env.company
    )
    
    @api.model
    def _get_options_groupby_fields(self, options):
        ''' Helper to retrieve all selected groupby fields.
        :param options:     The current report options.
        :return:            A list of valid fields on which perform the horizontal groupby.
        '''
        if not options.get('ir_filters'):
            return []

        AccountMoveLine = self.env['account.move.line']
        groupby_fields = []
        for option in options['ir_filters']:
            if not option['selected']:
                continue

            selected_fields = option['groupby']
            for field in selected_fields:
                if field in AccountMoveLine._fields and self._is_allowed_groupby_field(AccountMoveLine._fields[field]):
                    groupby_fields.append(field)
        return groupby_fields

    def _get_options(self, previous_options=None):
        # OVERRIDE
        options = super(ReportAccountReportInherit,
                        self)._get_options(previous_options)
        # If manual values were stored in the context, we store them as options.
        # This is useful for report printing, were relying only on the context is
        # not enough, because of the use of a route to download the report (causing
        # a context loss, but keeping the options).
        if self.allow_txt_generation == '20':
            options['change_header'] = True
        return options

    def _init_options_buttons(self, options, previous_options=None):
        if self.allow_txt_generation == '20':
            options['buttons'] = [
                {'name': _('PDF'), 'sequence': 10, 'action': 'export_file',
                 'action_param': 'export_to_pdf', 'file_export_type': _('PDF')},
                {'name': _('XLSX'), 'sequence': 20, 'action': 'export_file',
                 'action_param': 'export_to_xlsx', 'file_export_type': _('XLSX')},
                {'name': _('Save'), 'sequence': 100,
                 'action': 'open_report_export_wizard'},
                {'name': _('Exportar a txt'), 'sequence': 120,
                 'action': 'open_report_export_txt_wizard'}
            ]
        else:
            options['buttons'] = [
                {'name': _('PDF'), 'sequence': 10, 'action': 'export_file',
                 'action_param': 'export_to_pdf', 'file_export_type': _('PDF')},
                {'name': _('XLSX'), 'sequence': 20, 'action': 'export_file',
                 'action_param': 'export_to_xlsx', 'file_export_type': _('XLSX')},
                {'name': _('Save'), 'sequence': 100,
                 'action': 'open_report_export_wizard'},
            ]

    def open_report_export_txt_wizard(self, options):
        self.ensure_one()        
        new_context = {
            **self.env.context,
            'account_report_generation_options': options,
            'default_report_id': self.id,
        }        
        view_id = self.env.ref(
            'ple_inv_and_bal_0320_ee.wizard_report_generate_txt_view').id        
        new_wizard = self.with_context(new_context).env['wizard.report.generate.txt'].create({
            'report_model': self._name,            
            'report_id': self.id,
        })
        return {
            'type': 'ir.actions.act_window',
            'name': _('Export'),
            'view_mode': 'form',
            'res_model': 'wizard.report.generate.txt',
            'res_id': new_wizard.id,
            'target': 'new',
            'views': [[view_id, 'form']],
            'context': new_context,
        }
    def get_pdf(self, options):
               
        if self.allow_txt_generation != '20':
            return super(ReportAccountReportInherit, self).get_pdf(options)
        if not config['test_enable']:
            self = self.with_context(commit_assetsbundle=True)
        base_url = self.env['ir.config_parameter'].sudo().get_param('report.url') or self.env[
            'ir.config_parameter'].sudo().get_param('web.base.url')
        rcontext = {
            'mode': 'print',
            'base_url': base_url,
            'company': self.env.company
        }
        body_html = self.with_context(print_mode=True).get_html(options)
        body = self.env['ir.ui.view']._render_template(
            "account_reports.print_template",
            values=dict(rcontext, body_html=body_html))
        body_string = str(body)
        special_header = self.env.ref(
            "ple_inv_and_bal_0320_ee.action_print_report_pdf", False)._render_qweb_html(self.id)[0]
        body_string = body_string.replace('<body class="o_account_reports_body_print">',
                                          '<body class="o_account_reports_body_print">' + special_header.decode())
        body = Markup(body_string)
        footer = self.env['ir.actions.report']._render_template(
            "web.internal_layout", values=rcontext)
        footer = self.env['ir.actions.report']._render_template("web.minimal_layout", values=dict(rcontext, subst=True,
                                                                                                  body=Markup(
                                                                                                      footer.decode())))
        landscape = False
        if len(self.with_context(print_mode=True).get_header(options)[-1]) > 5:
            landscape = True
        return self.env['ir.actions.report']._run_wkhtmltopdf(
            [body],
            footer=footer.decode(),
            landscape=landscape,
            specific_paperformat_args={
                'data-report-margin-top': 10,
                'data-report-header-spacing': 10
            }
        )
