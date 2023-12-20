from odoo import api, fields, models




class HrPayrollStructure(models.Model):
    _inherit = 'hr.payroll.structure'

    name = fields.Char(translate=True)
    max_percent = fields.Integer(string='Max.Salary Advance Percentage')
    advance_date = fields.Integer(string='Salary Advance-After days')


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    def _compute_employee_loans(self):
        """This compute the loan amount and total loans count of an employee.
            """
        self.loan_count = self.env['hr.loan'].search_count([('employee_id', '=', self.id)])

    def _compute_employee_other_discounts(self):
        """This compute the other discount and total other discount count of an employee.
            """
        self.other_disc_count = self.env['hr.other.discounts'].search_count([('employee_id', '=', self.id)])

    other_disc_count = fields.Integer(string="Other Discounts Count", compute='_compute_employee_other_discounts')
    loan_count = fields.Integer(string="Loan Count", compute='_compute_employee_loans')


class HrPayslipInput(models.Model):
    _inherit = 'hr.payslip.input'

    discount_line_ids = fields.Many2many('hr.other.discounts.line', string="Other Discounts Line")
    loan_line_ids = fields.Many2many('hr.loan.line', string="Loan Installment")


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    def get_inputs_data(self):
        res = super(HrPayslip, self).get_inputs_data()
        if not res:
            return res
        domain = [
            ('employee_id', '=', self.employee_id.id),
            ('state', '=', 'approve'),
            ('contract_id', '=', self.contract_id.id)
        ]
        lon_obj = self.env['hr.loan'].search(domain)
        discount_obj = self.env['hr.other.discounts'].search(domain)

        loan_line_ids = []
        dsc_line_ids = []

        for loan in lon_obj:
            loan_line_ids += loan.loan_lines.filtered(lambda x: x.date <= self.date_to and not x.paid and self.struct_id == x.struct_id and x.receivable > 0)
            
        for dis in discount_obj:
            dsc_line_ids += dis.discount_lines.filtered(lambda x: x.date <= self.date_to and not x.paid and self.struct_id == x.struct_id and x.receivable > 0)

        adv_salary_ids = self.env['hr.salary.advance'].search([('employee_id', '=', self.employee_id.id), ('state', '=', 'approve')])
        advance_amount = sum(adv_salary_ids.filtered(lambda x: x.date.month == self.date_from.month and x.date.year == self.date_from.year).mapped('advance'))
        for result in res:
            if result.get('code') == 'LO' and result.get('contract_id') == self.contract_id.id:
                result['amount'] = sum(loan_line.receivable for loan_line in loan_line_ids) if loan_line_ids else 0
                result['loan_line_ids'] = [(6, 0, map(lambda x: x.id, loan_line_ids))] if loan_line_ids else False

            if result.get('code') == 'ODE_001' and result.get('contract_id') == self.contract_id.id:
                result['amount'] = sum(discount_line.receivable for discount_line in dsc_line_ids) if dsc_line_ids else 0
                result['discount_line_ids'] = [(6, 0, map(lambda x: x.id, dsc_line_ids))] if dsc_line_ids else False

            if result.get('code') == 'SAR' and result.get('contract_id') == self.contract_id.id:
                result['amount'] = advance_amount
        return res
    
    def change_paid_payslip_loan_and_discount_lines(self, payslip, amount, data_lines):
        amount_final = amount
        for line in data_lines:
            if line.receivable < amount_final:
                amount_final -= line.receivable
                line.payment = line.amount
                if line.payment == line.amount:
                    line.write({'paid': True, 'payslip_id': payslip.id})
            else:
                line.payment += amount_final
                amount_final = 0
                if line.payment == line.amount:
                    line.write({'paid': True, 'payslip_id': payslip.id})
                break
        return amount_final
    
    def validate_loan_and_discount_lines(self, payslip, domain, loan_lines, discount_lines):
        if loan_lines:
            amount = amount_max = 0
            loan_line_ids = lines_loan = []
            lon_obj = self.env['hr.loan'].search(domain)
            
            for loan in lon_obj:
                loan_line_ids += loan.loan_lines.filtered(lambda x: not x.paid and self.struct_id == x.struct_id and x.receivable > 0)
                amount_max = sum(loan_line.receivable for loan_line in loan_line_ids) if loan_line_ids else 0
            
            amount = loan_lines[0].amount
            lines_loan = loan_lines[0].loan_line_ids
            
            if amount > amount_max and len(loan_line_ids):
                amount = amount_max
                loan_lines[0].write({'amount': amount})
                load_id = payslip.line_ids.filtered(lambda x: x.code == 'LO')
                if load_id:
                    load_id[0].write({'amount': amount})

            amount = self.change_paid_payslip_loan_and_discount_lines(payslip, amount, lines_loan)
                  
            if amount != 0:
                loan_line_ids.clear()
                for loan in lon_obj:
                    loan_line_ids += loan.loan_lines.filtered(lambda x: not x.paid and self.struct_id == x.struct_id and x.receivable > 0)
                    if loan_line_ids:
                        amount = self.change_paid_payslip_loan_and_discount_lines(payslip, amount, loan_line_ids)
                        loan_line_ids += [loan for loan in loan_lines[0].loan_line_ids]
                        loan_lines[0].write({'loan_line_ids': [(6, 0, map(lambda x: x.id, loan_line_ids))]})
                        
        if discount_lines:
            amount = amount_max = 0
            discount_line_ids = lines_discount = []
            discount_obj = self.env['hr.other.discounts'].search(domain)
            
            for disc in discount_obj:
                discount_line_ids += disc.discount_lines.filtered(lambda x: not x.paid and self.struct_id == x.struct_id and x.receivable > 0)
                amount_max = sum(disc_line.receivable for disc_line in discount_line_ids) if discount_line_ids else 0
            
            amount = discount_lines[0].amount
            lines_discount = discount_lines[0].discount_line_ids
            
            if amount > amount_max and len(discount_line_ids):
                amount = amount_max
                discount_lines[0].write({'amount': amount})
                disc_id = payslip.line_ids.filtered(lambda x: x.code == 'ODE_001')
                if disc_id:
                    disc_id[0].write({'amount': amount})
            
            amount = self.change_paid_payslip_loan_and_discount_lines(payslip, amount, lines_discount)
            
            if amount != 0:
                discount_line_ids.clear()
                for disc in discount_obj:
                    discount_line_ids += disc.discount_lines.filtered(lambda x: not x.paid and self.struct_id == x.struct_id and x.receivable > 0)
                    if discount_line_ids:
                        amount = self.change_paid_payslip_loan_and_discount_lines(payslip, amount, discount_line_ids)
                        discount_line_ids += [disc for disc in discount_lines[0].discount_line_ids]
                        discount_lines[0].write({'discount_line_ids': [(6, 0, map(lambda x: x.id, discount_line_ids))]})        
        return True
                                                     
    def action_payslip_done(self):
        super(HrPayslip, self).action_payslip_done()
        for payslip in self:
            if payslip.input_line_ids:
                domain = [
                    ('employee_id', '=', payslip.employee_id.id),
                    ('state', '=', 'approve'),
                    ('contract_id', '=', payslip.contract_id.id)
                ]
                loan_lines = payslip.input_line_ids.filtered(lambda x: x.code == 'LO' and x.contract_id.id == payslip.contract_id.id)
                discount_lines = payslip.input_line_ids.filtered(lambda x: x.code == 'ODE_001' and x.contract_id.id == payslip.contract_id.id)
                self.validate_loan_and_discount_lines(payslip, domain, loan_lines, discount_lines)
                        
    def action_payslip_cancel(self):
        super(HrPayslip, self).action_payslip_cancel()
        amount = 0

        contract = []
        for record in self:
            contract.append(record.contract_id.id)

        for line in self.input_line_ids:
                if line.code == 'LO' and line.contract_id.id in contract and line.loan_line_ids:
                    amount = line.amount
                    for loan in line.loan_line_ids:
                        if amount > loan.payment:
                            amount -= loan.payment
                            loan.write({'paid': False, 'payslip_id': False, 'payment': 0})
                        else:
                            loan.write({'paid': False, 'payslip_id': False, 'payment': loan.payment - amount})
                    line.loan_line_ids = False
                if line.code == 'ODE_001' and line.contract_id.id in contract and line.discount_line_ids:
                    amount = line.amount
                    for disc, loan in zip(line.discount_line_ids, line.loan_line_ids):
                        if amount > disc.payment:
                            amount -= disc.payment
                            loan.write({'paid': False, 'payslip_id': False, 'payment': 0})
                        else:
                            loan.write({'paid': False, 'payslip_id': False, 'payment': disc.payment - amount})
                    line.discount_line_ids = False

class HrPayslipInputType(models.Model):
    _inherit = 'hr.payslip.input.type'

    name = fields.Char(translate=True)


class HrPayrollStructureType(models.Model):
    _inherit = 'hr.payroll.structure.type'

    name = fields.Char(translate=True)
