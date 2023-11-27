from odoo import api, fields, models
from odoo.exceptions import ValidationError


class LifeInsurance(models.Model):
    _name = 'life.insurance'
    _description = 'Vida ley'

    name = fields.Char(
        string='Nombre de póliza',
        required=True
    )        
    contacts_id = fields.Many2one(
        comodel_name='res.partner',
        string='Entidades',
    )
    nro = fields.Char(string='N° Póliza')
    start_date = fields.Date(string='Fecha inicio vigencia')
    end_date = fields.Date(string='Fecha fin vigencia')
    hiring_term = fields.Char(string='Plazo de contratación')
    rate = fields.Float(
        string='Tasa',
        digits=(16, 4),
    )
    amount = fields.Float(string='Importe')
    employees_ids = fields.Many2many(
        comodel_name='hr.employee',
        string='Empleados',
    )

    @api.constrains('employees_ids', 'start_date', 'end_date')
    def _check_employee_conflicts(self):
        for insurance in self:
            for employee in insurance.employees_ids:
                conflicting_insurances_up = self.env['life.insurance'].search([
                    ('id', '!=', insurance.id),
                    ('employees_ids', 'in', employee.id),
                    '|',
                    ('end_date', '>=', insurance.end_date), 
                    ('end_date', '>=', insurance.start_date)
                ])
                conflicting_insurances_down=self.env['life.insurance'].search([
                    ('id', '!=', insurance.id),
                    ('employees_ids', 'in', employee.id),
                    '|',
                    ('start_date', '<=', insurance.end_date), 
                    ('start_date', '<=', insurance.start_date)
                ])
                if conflicting_insurances_up and conflicting_insurances_down:
                    raise ValidationError(f"El empleado {employee.name} tiene conflictos de fechas con otros seguros.")
              