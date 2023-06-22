from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import UserError

class PaymentAnticipatedLoan(models.TransientModel):
    _name = 'payment.anticipated.loan'
    _description = 'Add Payment Anticipated'

    employee_id = fields.Many2one(
        string='Empleado',
        comodel_name='hr.employee' 
    )
    payment_type = fields.Many2one(
        string='Tipo de pago',
        comodel_name='payment.type'
    )
    payment_date = fields.Date(
        string='Fecha de pago',
        default=fields.Date.today()
    )
    voucher_number = fields.Char(
        string='Número de voucher'
    )
    amount = fields.Float(
        string='Monto'
    )
    loan_lines_ids = fields.One2many(
        string='Cuotas pendientes',
        comodel_name='payment.anticipated.loan.line',
        inverse_name='payment_anticipated_loan_id'
    )
        
    @api.constrains('amount')
    def constrains_amount(self):
        total_payment = 0
        for loan in self:
            for line in loan.loan_lines_ids:
                total_payment += line.payment
            if loan.amount != total_payment:
                raise UserError('El "Monto del pago anticipado" (%s) es diferente a la suma del "Abono de cada línea de cuota pendiente" (%s)') %(loan.amount, total_payment)
                
                
    def create_payment_anticipated(self):
        self.ensure_one()
        for loan in self:
            if loan.amount != 0:
                for line in loan.loan_lines_ids:
                    if line.payment > 0 and line.loan_lines_id:
                        payment = line.loan_lines_id.payment
                        receivable = line.loan_lines_id.receivable
                        line.loan_lines_id.write({
                            'payment': payment + line.payment,
                            'receivable': receivable - line.payment
                        })
                        if line.receivable == line.payment:
                            line.loan_lines_id.write({
                                'paid': True
                            })
                    if line.payment > 0 and line.discount_lines_id:
                        payment = line.discount_lines_id.payment
                        receivable = line.discount_lines_id.receivable
                        line.discount_lines_id.write({
                            'payment': payment + line.payment,
                            'receivable': receivable - line.payment
                        })
                        if line.receivable == line.payment:
                            line.discount_lines_id.write({
                                'paid': True
                            })
                return True                
            else:
                raise UserError('El "Monto del pago anticipado" debe ser mayor a 0')                
            

    
class PaymentAnticipatedLoanLine(models.TransientModel):
    _name = 'payment.anticipated.loan.line'
    _description = 'Add Payment Anticipated Line'
    
    payment_anticipated_loan_id = fields.Many2one(
        string='Pago anticipado',
        comodel_name='payment.anticipated.loan'
    )
    date = fields.Date(
        string= 'Fecha de pago'
    )
    amount = fields.Float(
        string='Monto', 
        default=0
    )
    paid = fields.Boolean(
        string='Pagado'
    )
    employee_id = fields.Many2one(
        string='Empleado',
        comodel_name='hr.employee'
    )
    payment = fields.Float(
        string='Abono', 
        default=0,
        store=True
    )
    receivable = fields.Float(
        string='Por pagar',
        default=0,
        readonly=True
    )
    struct_id = fields.Many2one(
        string='Estructura salarial',
        comodel_name='hr.payroll.structure'
    )
    loan_lines_id = fields.Many2one(
        string='Lineas de prestamo',
        comodel_name='hr.loan.line'
    )
    discount_lines_id = fields.Many2one(
        string='Lineas de otros descuentos',
        comodel_name='hr.other.discounts.line'
    )
    
    @api.onchange('payment')
    def _onchange_payment(self):
        for loan in self:
            if loan.payment != 0 and loan.payment > loan.receivable:
                raise UserError('El "Monto abonado" (%s) debe ser menor o igual al monto "Por pagar" (%s)') %(loan.payment, loan.receivable)
