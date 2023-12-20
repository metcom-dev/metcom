from odoo import api, fields, models
from odoo.exceptions import ValidationError


class DataUtilities(models.Model):
    _name = 'data.utilities'
    _description = 'Proceso de Utilidades'

    date_from = fields.Date(
        string='Fecha de Inicio',
        required=True
    )
    date_to = fields.Date(
        string='Fecha de Fin',
        required=True
    )
    annual_rent_before_tax = fields.Float(
        string='Renta anual antes de Impuesto'
    )
    percent = fields.Float(
        string='Porcentaje de participación'
    )
    amount = fields.Float(
        string='Monto de participación',
        readonly=True
    )
    nro_employees = fields.Integer(
        string='N° de trabajadores',
        readonly=True
    )
    nro_days = fields.Integer(
        string='N° Total de días laborados por todos los trabajadores',
        readonly=True
    )
    total_amount = fields.Float(
        string='Total remuneraciones computable de todos los trabajadores',
        readonly=True
    )
    factor_days = fields.Float(
        string='Factor días laborados',
        readonly=True,
        digits=(12, 6)
    )
    factor_amount = fields.Float(
        string='Factor remuneración',
        readonly=True,
        digits=(12, 6)
    )
    is_active = fields.Boolean(
        string='Activo',
        default=True
    )
    difference = fields.Float(
        string='Diferencia monto de participación',
        help='Este campo se utiliza cuando nos indican el importe de la renta ya calculado.'
    )

    @api.model
    def create(self, vals):
        self.check_is_active(vals)
        return super(DataUtilities, self).create(vals)

    def write(self, vals):
        self.check_is_active(vals)
        return super(DataUtilities, self).write(vals)

    def check_is_active(self, vals):
        if vals.get('is_active'):
            recs = self.search([('is_active', '=', True)])
            if recs:
                raise ValidationError('Ya existe un registro activo.')

    def compute_fields(self):
        if self.date_from >= self.date_to:
            raise ValidationError('La fecha "Desde" no puede ser menor o igual que la fecha "Hasta".')
        if self.date_from.strftime('%Y') != self.date_to.strftime('%Y'):
            raise ValidationError('La fechas del periodo deben pertenecer al mismo año.')

        hr_payslip_line = self.env['hr.payslip.line']
        worked_days = self.env['hr.payslip.worked_days']
        if self.difference != 0:
            self.amount = self.difference
        else:
            self.amount = self.annual_rent_before_tax * self.percent
        start_y = int(self.date_from.strftime('%Y'))
        start_m = int(self.date_from.strftime('%m'))
        end_y = int(self.date_to.strftime('%Y'))
        end_m = int(self.date_to.strftime('%m'))
        periods = hr_payslip_line._get_periods(start_m, start_y, end_m, end_y)

        payslips = hr_payslip_line.search([('date_start', 'in', periods)])
        payslips_utilities = payslips.filtered(lambda x: x.salary_rule_id and x.salary_rule_id.utilities)
        payslip_days = worked_days.search([('date_start', 'in', periods), ('code', 'in', ['DDO', 'GLOBAL', 'WORK100'])])
        nro_employees = len(payslips.mapped('employee_id'))

        self.nro_employees = nro_employees
        self.nro_days = sum(line.number_of_days for line in payslip_days)
        self.total_amount = sum(line.amount for line in payslips_utilities)
        self.factor_days = self.amount / 2 / self.nro_days if self.nro_days != 0 else 0
        self.factor_amount = self.amount / 2 / self.total_amount if self.total_amount != 0 else 0

    def name_get(self):
        return [(obj.id, '{}-{}{}'.format(obj.date_to, obj.date_from, ' - ACTIVO' if obj.is_active else '')) for obj in self]
