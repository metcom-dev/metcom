from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from collections import defaultdict
from odoo.tools import float_compare, float_is_zero


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    def _prepare_adjust_line(self, line_ids, adjust_type, debit_sum, credit_sum, date):
        if self.journal_id.type == 'general':
            if (0.0 if adjust_type == 'credit' else credit_sum - debit_sum) > 0:
                acc_id = self.journal_id.default_debit_account_id.id
            else:
                acc_id = self.journal_id.default_credit_account_id.id
        else:
            acc_id = self.journal_id.default_account_id.id

        if not acc_id:
            raise UserError(
                _('The Expense Journal "%s" has not properly configured the default Account!') % (self.journal_id.name))
        existing_adjustment_line = (
            line_id for line_id in line_ids if line_id['name'] == _('Adjustment Entry')
        )
        adjust_credit = next(existing_adjustment_line, False)

        if not adjust_credit:
            adjust_credit = {
                'name': _('Adjustment Entry'),
                'partner_id': self.employee_id.address_home_id.id,
                'account_id': acc_id,
                'journal_id': self.journal_id.id,
                'date': date,
                'debit': 0.0 if adjust_type == 'credit' else credit_sum - debit_sum,
                'credit': debit_sum - credit_sum if adjust_type == 'credit' else 0.0,
            }
            line_ids.append(adjust_credit)
        else:
            adjust_credit['credit'] = debit_sum - credit_sum


    def _action_create_account_move(self):
        precision = self.env['decimal.precision'].precision_get('Payroll')
        # Add payslip without run
        payslips_to_post = self.filtered(lambda x: not x.payslip_run_id)
        # Adding pay slips from a batch and deleting pay slips with a batch that is not ready for validation.
        payslip_runs = (self - payslips_to_post).mapped('payslip_run_id')
        for run in payslip_runs:
            payslips_to_post |= run.slip_ids
        # A payslip need to have a done state and not an accounting move.
        payslips_to_post = payslips_to_post.filtered(lambda slip: slip.state == 'done' and not slip.move_id)
        # Check that a journal exists on all the structures
        if any(not payslip.struct_id for payslip in payslips_to_post):
            raise ValidationError(_('One of the contract for these payslips has no structure type.'))
        if any(not structure.journal_id for structure in payslips_to_post.mapped('struct_id')):
            raise ValidationError(_('One of the payroll structures has no account journal defined on it.'))
        # Map all payslips by structure journal and pay slips month.
        # {'journal_id': {'month': [slip_ids]}}
        slip_mapped_data = defaultdict(lambda: defaultdict(lambda: self.env['hr.payslip']))
        for slip in payslips_to_post:
            slip_mapped_data[slip.struct_id.journal_id.id][fields.Date().end_of(slip.date_to, 'month')] |= slip
        for journal_id in slip_mapped_data:  # For each journal_id.
            for slip_date in slip_mapped_data[journal_id]:  # For each month.
                for slip in slip_mapped_data[journal_id][slip_date]:
                    line_ids = []
                    debit_sum = 0.0
                    credit_sum = 0.0
                    date = slip_date
                    move_dict = {
                        'narration': slip.number or '' + ' - ' + slip.employee_id.name or '',
                        'journal_id': journal_id,
                        'date': date,
                        'ref': slip.number
                    }

                    slip_lines = slip._prepare_slip_lines(date, line_ids)
                    line_ids.extend(slip_lines)
                    # Get the debit and credit sum and partner_id.
                    for line_id in line_ids:
                        if any(slip.employee_id.partner_concept_ids):
                            for partner_concept in slip.employee_id.partner_concept_ids:
                                start_date = partner_concept.start_date if partner_concept.start_date else False
                                end_date = partner_concept.end_date if partner_concept.end_date else False
                                if start_date and end_date:
                                    check_date_range = True if slip.date_from >= start_date and slip.date_to <= end_date else False
                                elif start_date and not end_date:
                                    check_date_range = True if slip.date_from >= start_date else False
                                elif not start_date and end_date:
                                    check_date_range = True if slip.date_to <= end_date else False
                                else:
                                    check_date_range = True
                                if partner_concept.is_active and line_id['name'] == partner_concept.salary_rule.name and check_date_range:
                                    if (partner_concept.debit and not partner_concept.credit and line_id['debit'] > 0) or (
                                        not partner_concept.debit and partner_concept.credit and line_id['credit'] > 0) or (
                                            partner_concept.debit and partner_concept.credit):
                                        line_id['partner_id'] = partner_concept.partner_id.id
                                        break
                                    else:
                                        line_id['partner_id'] = slip.employee_id.address_home_id.id
                                        break
                                else:
                                    line_id['partner_id'] = slip.employee_id.address_home_id.id
                        else:
                            line_id['partner_id'] = slip.employee_id.address_home_id.id
                        debit_sum += line_id['debit']
                        credit_sum += line_id['credit']
                    # The code below is called if there is an error in the balance between credit and debit sum.
                    if float_compare(credit_sum, debit_sum, precision_digits=precision) == -1:
                        slip._prepare_adjust_line(line_ids, 'credit', debit_sum, credit_sum, date)
                    elif float_compare(debit_sum, credit_sum, precision_digits=precision) == -1:
                        slip._prepare_adjust_line(line_ids, 'debit', debit_sum, credit_sum, date)
                    # Add accounting lines in the move
                    move_dict['line_ids'] = [(0, 0, line_vals) for line_vals in line_ids]
                    move = self._create_account_move(move_dict)
                    slip.write({'move_id': move.id, 'date': date})
        return True

    def _prepare_slip_lines(self, date, line_ids):
        self.ensure_one()
        precision = self.env['decimal.precision'].precision_get('Payroll')
        new_lines = []
        for line in self.line_ids.filtered(lambda line: line.category_id):
            amount = -line.total if self.credit_note else line.total
            if line.code == 'NET':  # Check if the line is the 'Net Salary'.
                for tmp_line in self.line_ids.filtered(lambda line: line.category_id):
                    if tmp_line.salary_rule_id.not_computed_in_net:  # Check if the rule must be computed in the 'Net Salary' or not.
                        if amount > 0:
                            amount -= abs(tmp_line.total)
                        elif amount < 0:
                            amount += abs(tmp_line.total)
            if float_is_zero(amount, precision_digits=precision):
                continue
            debit_account_id = line.salary_rule_id.account_debit.id
            credit_account_id = line.salary_rule_id.account_credit.id

            if debit_account_id:  # If the rule has a debit account.
                debit = amount if amount > 0.0 else 0.0
                credit = -amount if amount < 0.0 else 0.0

                debit_line = self._get_existing_lines(
                    line_ids + new_lines, line, debit_account_id, debit, credit)

                if not debit_line:
                    debit_line = self._prepare_line_values(line, debit_account_id, date, debit, credit)
                    debit_line['tax_ids'] = [(4, tax_id) for tax_id in line.salary_rule_id.account_debit.tax_ids.ids]
                    new_lines.append(debit_line)
                else:
                    debit_line['debit'] += debit
                    debit_line['credit'] += credit

            if credit_account_id:  # If the rule has a credit account.
                debit = -amount if amount < 0.0 else 0.0
                credit = amount if amount > 0.0 else 0.0
                credit_line = self._get_existing_lines(
                    line_ids + new_lines, line, credit_account_id, debit, credit)

                if not credit_line:
                    credit_line = self._prepare_line_values(line, credit_account_id, date, debit, credit)
                    credit_line['tax_ids'] = [(4, tax_id) for tax_id in line.salary_rule_id.account_credit.tax_ids.ids]
                    new_lines.append(credit_line)
                else:
                    credit_line['debit'] += debit
                    credit_line['credit'] += credit
        return new_lines

    def _prepare_adjust_line(self, line_ids, adjust_type, debit_sum, credit_sum, date):
        acc_id = self.journal_id.default_account_id.id
        if not acc_id:
            raise UserError(
                _('The Expense Journal "%s" has not properly configured the default Account!') % (self.journal_id.name))
        existing_adjustment_line = (
            line_id for line_id in line_ids if line_id['name'] == _('Adjustment Entry')
        )
        adjust_credit = next(existing_adjustment_line, False)

        if not adjust_credit:
            adjust_credit = {
                'name': _('Adjustment Entry'),
                'partner_id': False,
                'account_id': acc_id,
                'journal_id': self.journal_id.id,
                'date': date,
                'debit': 0.0 if adjust_type == 'credit' else credit_sum - debit_sum,
                'credit': debit_sum - credit_sum if adjust_type == 'credit' else 0.0,
            }
            line_ids.append(adjust_credit)
        else:
            adjust_credit['credit'] = debit_sum - credit_sum

    def _create_account_move(self, values):
        return self.env['account.move'].create(values)
