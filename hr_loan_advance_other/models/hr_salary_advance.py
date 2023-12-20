import time
import logging
from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import AccessError, Warning

_logger = logging.getLogger(__name__)


class HrSalaryAdvance(models.Model):
    _name = "hr.salary.advance"
    _description = _('Salary Advance')
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Name', readonly=True, default=lambda self: 'Adv/')
    reason = fields.Text(string='Reason')
    date = fields.Date(string='Date', required=True, default=lambda self: fields.Date.today())
    advance = fields.Float(string='Advance', required=True)
    exceed_condition = fields.Boolean(string='Exceed than maximum', help="The Advance is greater than the maximum percentage in salary structure")
    state = fields.Selection([('draft', 'Draft'),
                              ('submit', 'Submitted'),
                              ('waiting_approval', 'Waiting Approval'),
                              ('approve', 'Approved'),
                              ('paid', 'Paid'),
                              ('cancel', 'Cancelled'),
                              ('reject', 'Rejected')], string='Status', default='draft')
    employee_id = fields.Many2one(
        comodel_name='hr.employee',
        string='Employee',
        required=True
    )
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        string='Currency'
    )
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.user.company_id
    )
    payment_method = fields.Many2one(
        comodel_name='account.journal',
        string='Payment Method'
    )
    department = fields.Many2one(
        comodel_name='hr.department',
        string='Department'
    )
    debit = fields.Many2one(
        comodel_name='account.account',
        string='Debit Account'
    )
    credit = fields.Many2one(
        comodel_name='account.account',
        string='Credit Account'
    )
    journal = fields.Many2one(
        comodel_name='account.journal',
        string='Journal'
    )
    employee_contract_id = fields.Many2one(
        comodel_name='hr.contract',
        string='Contract'
    )
    move_id = fields.Many2one(
        comodel_name='account.move',
        string='Asiento Contable',
        readonly=True,
        copy=False
    )

    @api.onchange('employee_id')
    def onchange_employee_id(self):
        department_id = self.employee_id.department_id.id
        contract_id = self.get_contract(self.employee_id, self.date, self.date)
        domain = [('employee_id', '=', self.employee_id.id)]
        return {
            'value': {
                'department': department_id,
                'employee_contract_id': contract_id
            },
            'domain': {'employee_contract_id': domain}
        }

    @api.model
    def get_contract(self, employee, date_from, date_to):
        if not employee:
            return False
        if not date_to:
            date_to = date_from
        # a contract is valid if it ends between the given dates
        clause_1 = ['&', ('date_end', '<=', date_to), ('date_end', '>=', date_from)]
        # OR if it starts between the given dates
        clause_2 = ['&', ('date_start', '<=', date_to), ('date_start', '>=', date_from)]
        # OR if it starts before the date_from and finish after the date_end (or never finish)
        clause_3 = ['&', ('date_start', '<=', date_from), '|', ('date_end', '=', False), ('date_end', '>=', date_to)]
        clause_final = [('employee_id', '=', employee.id), ('state', '=', 'open'), '|',
                        '|'] + clause_1 + clause_2 + clause_3
        contract = self.env['hr.contract'].search(clause_final, limit=1)
        return contract.id if contract else False

    @api.onchange('company_id')
    def onchange_company_id(self):
        company = self.company_id
        domain = [('company_id.id', '=', company.id)]
        result = {'domain': {'journal': domain}}
        return result

    def back_to_draft(self):
        self.ensure_one()
        self.state = 'draft'
        self.move_id = False

    def submit_to_manager(self):
        self.ensure_one()
        self.state = 'submit'

    def cancel(self):
        self.ensure_one()
        self.state = 'cancel'
        self.move_id = False

    def reject(self):
        self.ensure_one()
        self.state = 'reject'
        self.move_id = False

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].get('hr.salary.advance.seq') or ' '
        res_id = super(HrSalaryAdvance, self).create(vals)
        return res_id

    def approve_request(self):
        """This Approve the employee salary advance request. """
        self.ensure_one()
        emp_obj = self.env['hr.employee']
        address = emp_obj.browse([self.employee_id.id]).address_home_id
        if not address.id:
            raise AccessError('Define home address for employee')

        current_month = datetime.strptime(str(self.date), '%Y-%m-%d').date().month

        if not self.employee_contract_id:
            raise AccessError('Define a contract for the employee')
        struct_id = self.employee_contract_id.struct_id
        if not struct_id.max_percent or not struct_id.advance_date:
            raise AccessError('Max percentage or advance days are not provided in Contract')
        adv = self.advance
        amt = (self.employee_contract_id.struct_id.max_percent * self.employee_contract_id.wage) / 100
        if adv > amt and not self.exceed_condition:
            raise AccessError('Advance amount is greater than allotted')

        if not self.advance:
            raise AccessError('You must Enter the Salary Advance amount')
        payslip_obj = self.env['hr.payslip'].search([('employee_id', '=', self.employee_id.id),
                                                     ('state', '=', 'done'), ('date_from', '<=', self.date),
                                                     ('date_to', '>=', self.date)])
        if payslip_obj:
            raise AccessError('This month salary already calculated.')

        for slip in self.env['hr.payslip'].search([('employee_id', '=', self.employee_id.id)]):
            slip_moth = datetime.strptime(str(slip.date_from), '%Y-%m-%d').date().month
            if current_month == slip_moth + 1:
                slip_day = datetime.strptime(str(slip.date_from), '%Y-%m-%d').date().day
                current_day = datetime.strptime(str(self.date), '%Y-%m-%d').date().day
                if current_day - slip_day < struct_id.advance_date:
                    raise Warning(_('Request can be done after "%s" Days From previous month salary') % struct_id.advance_date)
        self.state = 'waiting_approval'

    def approve_request_acc_dept(self):
        """This Approve the employee salary advance request from accounting department.
                   """
        self.ensure_one()
        if not self.debit or not self.credit or not self.journal:
            raise AccessError("You must enter Debit & Credit account and journal to approve.")
        if not self.advance:
            raise AccessError("You must Enter the Salary Advance amount.")

        self.state = 'approve'
        self.update_seat()
        if self.move_id:
            return True

        move_obj = self.env['account.move'].with_context(default_type='entry')
        timenow = time.strftime('%Y-%m-%d')
        line_ids = []
        debit_sum = 0.0
        credit_sum = 0.0
        for request in self:
            amount = request.advance
            request_name = request.employee_id.name
            partner_id = request.employee_id.address_home_id.id or False
            reference = request.name
            journal_id = request.journal.id
            move = {
                'ref': reference,
                'journal_id': journal_id,
                'date': timenow
            }

            debit_account_id = request.debit.id
            credit_account_id = request.credit.id

            if debit_account_id:
                debit_line = (0, 0, {
                    'name': request_name,
                    'account_id': debit_account_id,
                    'journal_id': journal_id,
                    'partner_id': partner_id,
                    'date': timenow,
                    'debit': amount > 0.0 and amount or 0.0,
                    'credit': amount < 0.0 and -amount or 0.0,
                    'currency_id': self.currency_id and self.currency_id.id,
                })
                line_ids.append(debit_line)
                debit_sum += debit_line[2]['debit'] - debit_line[2]['credit']

            if credit_account_id:
                credit_line = (0, 0, {
                    'name': request_name,
                    'account_id': credit_account_id,
                    'journal_id': journal_id,
                    'partner_id': partner_id,
                    'date': timenow,
                    'debit': amount < 0.0 and -amount or 0.0,
                    'credit': amount > 0.0 and amount or 0.0,
                    'currency_id': self.currency_id and self.currency_id.id,
                })
                line_ids.append(credit_line)
                credit_sum += credit_line[2]['credit'] - credit_line[2]['debit']

            move.update({'line_ids': line_ids})
            new_move = move_obj.create(move)
            
            try:
                new_move.action_post()
            except Exception:
                _logger.debug('Error publishing move: {}'.format(move_obj))
            self.update_seat()
        return True

    def update_seat(self):
        for record in self:
            move_obj = self.env['account.move'].search([('ref', '=', record.name)])
            self.write({'move_id':move_obj.id if move_obj else False})
        return True
    
class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'
    
    @api.depends('full_reconcile_id.name', 'matched_debit_ids', 'matched_credit_ids')
    def _compute_matching_number(self):
        res = super(AccountMoveLine,self)._compute_matching_number()
        
        for record in self:
            if record.full_reconcile_id:
                record.matching_number = record.full_reconcile_id.name
            elif record.matched_debit_ids or record.matched_credit_ids:
                record.matching_number = 'P'
            else:
                record.matching_number = None
        
            match = record.matching_number
            if match and match != 'P' and match != False:
                self.env.cr.execute("""
                    UPDATE hr_salary_advance AS sa
                    SET state = 'paid'
                    FROM hr_payslip AS hp
                    WHERE sa.employee_id IS NOT NULL
                        AND sa.state = 'approve'
                        AND sa.employee_id = hp.employee_id
                        AND hp.state = 'done'
                        AND EXISTS (
                            SELECT 1
                            FROM account_move_line AS aml
                            WHERE aml.move_id = hp.move_id
                        AND aml.matching_number IS NOT NULL
                        AND aml.matching_number != 'P'
                        AND (aml.matching_number != 'None' OR aml.matching_number != 'False')
                        AND aml.name = 'Adelanto de sueldo'
                        );
                """)
            
                self.env.cr.execute("""
                    SELECT
                        hl.move_id AS move_id,
                        MAX(hl.installment) AS max_installment,
                        hl.loan_amount,
                        hl.amount_paid,
                        hl.amount_owed,
                        COUNT(CASE WHEN aml.matching_number IS NOT NULL AND aml.matching_number <> 'P' THEN 1 ELSE NULL END) AS reconciled_installments,
                        hl.state
                    FROM hr_loan AS hl
                    INNER JOIN account_move_line AS aml ON hl.move_id = aml.move_id
                    WHERE hl.move_id = %s
                    GROUP BY hl.move_id, hl.loan_amount, hl.amount_paid, hl.amount_owed, hl.state;    
                """,(record.move_id.id,))
            
                results = self.env.cr.fetchall()
                        
                if results:
                    for record in results:                   
                        move_id,max_installment,loan_amount,amount_paid,amount_owed,reconciled,state = record        
                        if state != 'paid':
                            reconciled +=1                               
                            res = loan_amount / max_installment
                            amount_paid = res * reconciled
                            amount_owed = loan_amount - amount_paid            
                        if max_installment == reconciled:                  
                            state = 'paid'             
                        hr_loan = self.env['hr.loan'].search([('move_id', '=', move_id)])
                        if hr_loan:
                            hr_loan.write({'state': state, 'amount_paid': amount_paid, 'amount_owed': amount_owed})
                                                 
        return res
    
    
        