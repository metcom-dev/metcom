from odoo import api, fields, models


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    judicial_discount = fields.Float(
        string='Descuento judicial',
        groups="hr.group_hr_user"
    )
    judicial_discount_percent = fields.Float(
        string='Descuento judicial porcentaje',
        groups="hr.group_hr_user"
    )
    exists_beneficiary = fields.Boolean(
        string='Existe Beneficiario?',
        groups="hr.group_hr_user"
    )
    beneficiary = fields.Many2one(
        'res.partner', 'Beneficiario',
        help='Enter here the private address of the employee, not the one linked to your company.',
        groups="hr.group_hr_user", tracking=True,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")

    bond = fields.Char(
        string='Vínculo',
        size=10,
        groups="hr.group_hr_user"
    )
    card_type_id = fields.Many2one(
        comodel_name="l10n_latam.identification.type",
        string='Tipo de doc.',
        groups="hr.group_hr_user")
    card_id = fields.Char(
        string='N° doc.',
        groups="hr.group_hr_user"
    )
    payment_type = fields.Many2one(
        comodel_name='payment.type',
        string='Tipo de Pago',
        groups="hr.group_hr_user"
    )
    pay_code = fields.Char(
        string="Journal Code",
        related="payment_type.code",
        groups="hr.group_hr_user"
    )

    settlement_retention = fields.Boolean(
        string='Retener Liquidacion?',
        groups="hr.group_hr_user",
        default=False
    )
    retention_on = fields.Selection([
        ('total_income', 'Ingresos totales'),
        ('affection_income', 'Ingreso Afecto'),
        ('unaffected_income', 'Ingreso No Afecto'),
        ('net_income', 'Ingreso neto'),
        ('net_payable', 'Neto a pagar'),
    ],
        string="Retención sobre",
        groups="hr.group_hr_user"
    )
    account_number = fields.Many2one('res.partner.bank', "Numero de cuenta", groups="hr.group_hr_user")
    bank = fields.Char(compute="_name_bank", string='Banco', readonly=True, groups="hr.group_hr_user")
    cci = fields.Char(compute="_mostrarcci", string='CCI', readonly=True, groups="hr.group_hr_user")
    start_date = fields.Date(string='Vigencia:Desde', groups="hr.group_hr_user")
    end_date = fields.Date(string='Hasta', groups="hr.group_hr_user")
    retention_amount = fields.Float(string="Importe Tope de retención", default=0, groups="hr.group_hr_user")

    @api.depends('account_number')
    def _mostrarcci(self):
        for employee in self:
            if employee.account_number:
                employee.cci = employee.account_number.cci
            else:
                employee.cci = ' '

    @api.depends('account_number')
    def _name_bank(self):
        for employee in self:
            if employee.account_number and employee.account_number.bank_id:
                employee.bank = employee.account_number.bank_id.name
            else:
                employee.bank = ' '
