from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    state = fields.Selection(selection_add=[('paid', u'Pagado')])
    state_move = fields.Char(compute='_compute_state_move')

    @api.depends('move_id', 'move_id.state')
    def _compute_state_move(self):
        for move in self:
            if move.move_id:
                move.state_move = move.move_id.state
            else:
                move.state_move = 'False'

    def action_move_id_post(self):
        for move in self.move_id:
            if move.state == 'draft':
                move.action_post()


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    default_credit_account_id = fields.Many2one(
        'account.account',
        string='Cuenta acreedora por defecto',
        domain=[('deprecated', '=', False)]
    )
    default_debit_account_id = fields.Many2one(
        'account.account',
        string='Cuenta deudora por defecto',
        domain="[('deprecated', '=', False), ('company_id', '=', company_id)]"
    )
    sequence_number_next = fields.Integer(
        string='Próximo número'
    )


class HrMassivePayment(models.Model):
    _inherit = 'hr.massive.payment'

    move_id = fields.Many2one(
        comodel_name='account.move',
        string='Asiento Contable',
        readonly=True
    )
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('paid', 'Pagado')],
        string='Estado',
        default='draft'
    )
    has_reconciled_entries = fields.Boolean(
        string='Tiene asientos conciliados',
        compute='_compute_has_reconciled_entries'
    )

    @api.depends(
        'move_id',
        'move_id.line_ids',
        'payslip_ids',
        'payslip_ids.move_id',
        'payslip_ids.move_id.line_ids')
    def _compute_has_reconciled_entries(self):
        for payment in self:
            account_move_line, ids = self.search_reconcile_line()
            payment.has_reconciled_entries = len(account_move_line) > 1

    def action_payslip_paid(self):
        if not self.payslip_ids:
            raise ValidationError('Debe seleccionar nóminas primero.')
        if self.move_id:
            raise ValidationError('Ya existe un asiento contable relacionado.')

        line_ids = []
        line_ids_payslip = []
        net = self.env.ref('hr_payroll.NET', False)
        date = fields.Date.today()
        ref = u'Asiento de conciliación planilla'
        journal_id = self.payslip_ids[0].journal_id
        currency_id = self.env.user.company_id.currency_id
        move_dict = {
            'ref': ref,
            'journal_id': journal_id.id,
            'date': date,
        }
        debit_sum = 0.0
        credit_sum = 0.0

        debit_account_id_general = False
        credit_account_id_general = False
        journal_general = False
        for slip in self.payslip_ids.filtered(lambda x: x.move_id):
            currency = slip.company_id.currency_id or slip.journal_id.company_id.currency_id
            net_lines = slip.line_ids.filtered(lambda x: x.category_id == net)
            net_amount = sum(line.total for line in net_lines)
            amount = currency.round(net_amount)
            if currency.is_zero(amount):
                continue

            debit_account_id = net_lines[0].salary_rule_id.account_debit
            credit_account_id = net_lines[0].salary_rule_id.account_credit
            debit_account_id_general = debit_account_id
            credit_account_id_general = credit_account_id
            journal_general = slip.journal_id
            if not debit_account_id and not credit_account_id:
                continue
            if credit_account_id:
                debit_line = (0, 0, {
                    'name': slip.name + ' NETO',
                    'partner_id': slip.employee_id.address_home_id.id,
                    'account_id': credit_account_id.id,
                    'journal_id': slip.journal_id.id,
                    'date': date,
                    'debit': amount > 0.0 and amount or 0.0,
                    'credit': amount < 0.0 and -amount or 0.0,
                    'analytic_account_id': slip.contract_id.analytic_account_id.id,
                })
                line_ids.append(debit_line)
                debit_sum += debit_line[2]['debit'] - debit_line[2]['credit']
            if debit_account_id:
                credit_line = (0, 0, {
                    'name': slip.name + ' NETO',
                    'partner_id': slip.employee_id.address_home_id.id,
                    'account_id': debit_account_id.id,
                    'journal_id': slip.journal_id.id,
                    'date': date,
                    'debit': amount < 0.0 and -amount or 0.0,
                    'credit': amount > 0.0 and amount or 0.0,
                    'analytic_account_id': slip.contract_id.analytic_account_id.id,
                })
                line_ids.append(credit_line)
                credit_sum += credit_line[2]['credit'] - credit_line[2]['debit']
            slip.state = 'paid'

        debit_line = (0, 0, {
            'name': 'Pago Planilla',
            'partner_id': False,
            'account_id': credit_account_id_general.id,
            'journal_id': journal_general.id,
            'date': date,
            'debit': debit_sum > 0.0 and debit_sum or 0.0,
            'credit': credit_sum < 0.0 and -credit_sum or 0.0,
        })
        line_ids_payslip.append(debit_line)

        credit_line = (0, 0, {
            'name': 'Pago Planilla',
            'partner_id': False,
            'account_id': credit_account_id_general.id,
            'journal_id': journal_general.id,
            'date': date,
            'debit': debit_sum < 0.0 and -debit_sum or 0.0,
            'credit': credit_sum > 0.0 and credit_sum or 0.0,
        })
        line_ids_payslip.append(credit_line)

        if currency_id.compare_amounts(credit_sum, debit_sum) == -1:
            acc_id = journal_id.default_credit_account_id.id
            if not acc_id:
                raise ValidationError('The Expense Journal "%s" has not properly configured the Credit Account!' %
                                      journal_id.name)
            adjust_credit = (0, 0, {
                'name': 'Adjustment Entry',
                'partner_id': False,
                'account_id': acc_id,
                'journal_id': journal_id.id,
                'date': date,
                'debit': 0.0,
                'credit': currency_id.round(debit_sum - credit_sum),
            })
            line_ids.append(adjust_credit)
            line_ids_payslip.append(adjust_credit)
        elif currency_id.compare_amounts(debit_sum, credit_sum) == -1:
            acc_id = journal_id.default_debit_account_id.id
            if not acc_id:
                raise ValidationError('The Expense Journal "%s" has not properly configured the Debit Account!' %
                                      journal_id.name)
            adjust_debit = (0, 0, {
                'name': 'Adjustment Entry',
                'partner_id': False,
                'account_id': acc_id,
                'journal_id': journal_id.id,
                'date': date,
                'debit': currency_id.round(credit_sum - debit_sum),
                'credit': 0.0,
            })
            line_ids.append(adjust_debit)
            line_ids_payslip.append(adjust_debit)
        move_dict['line_ids'] = line_ids_payslip
        move = self.env['account.move'].create(move_dict)
        self.write({'move_id': move.id, 'state': 'paid'})
        move.action_post()

    def search_reconcile_line(self):
        account_move_line = self.env['account.move.line']
        ids = []
        for line in self.move_id.line_ids.filtered(lambda x: x.account_id.reconcile):
            if line.reconciled:
                account_move_line |= line
            ids.append(line.id)
        for payslip in self.payslip_ids:
            for line in payslip.move_id.line_ids.filtered(lambda x: x.account_id.reconcile and x.reconciled):
                account_move_line |= line
                ids.append(line.id)
        return account_move_line, ids

    def reconciled_lines(self):
        net = self.env.ref('hr_payroll.NET', False)
        lines_reconcile = self.env['account.move.line']
        for line in self.move_id.line_ids.filtered(lambda x: x.debit > 0):
            lines_reconcile |= line
        for payslip in self.payslip_ids:
            name = 'Salario neto'
            for slip in payslip.line_ids.filtered(lambda x: x.category_id == net):
                name = slip.name
                break
            for line in payslip.move_id.line_ids.filtered(lambda x: x.name == name and x.credit > 0):
                lines_reconcile |= line
        lines_reconcile = lines_reconcile.filtered_domain([('reconciled', '=', False)])
        return lines_reconcile

    def action_reconciled(self):
        for payslip in self.payslip_ids:
            if payslip.move_id.state != 'posted':
                raise UserError(
                    "Algunos de los asientos del presente lote no estan publicado. Por favor proceda a su publicacion para continuar")
        lines_reconcile = self.reconciled_lines()
        lines_reconcile.reconcile()
        return True

    def open_reconcile_view(self):
        action = self.env['ir.actions.act_window']._for_xml_id('account.action_account_moves_all_a')
        account_move_line, ids = self.search_reconcile_line()
        action['domain'] = [('id', 'in', ids)]
        return action

    def action_break_reconciled(self):
        account_move_line, ids = self.search_reconcile_line()
        account_move_line.remove_move_reconcile()
        return True

    def action_payslip_draft(self):
        self.action_break_reconciled()
        self.move_id.button_cancel()
        self.move_id.with_context(force_delete=True).unlink()
        for slip in self.payslip_ids.filtered(lambda x: x.move_id):
            slip.state = 'done'
        self.state = 'draft'
