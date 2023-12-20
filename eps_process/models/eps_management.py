from odoo import models, fields, api
from odoo.exceptions import ValidationError

class EpsManagement(models.Model):
    _name = "eps.management"
    _description = "EPS management"

    star_date = fields.Date(string='Fecha de inicio', required=True)
    finish_date = fields.Date(string='Fecha de finalización', required=True)
    entity = fields.Char(string='Entidad', required=True)
    partner_id = fields.Many2one(comodel_name='res.partner', string='Entidad', required=True)
    insurance = fields.Char(string='N° de poliza')
    rate_employer = fields.Float(string='Porcentaje Empleador')
    amount_employer = fields.Float(string='Importe Empleador')
    rate_worker = fields.Float(string='Porcentaje Trabajador')
    amount_worker = fields.Float(string='Importe Trabajador')
    employeer_ids = fields.Many2many(
    comodel_name='hr.employee',
    string='Empleados')
    _writing_employees = fields.Boolean(default=False, readonly=False)

    def name_get(self):
        res = []
        for _ in self:
            name = "%s-%s" % (_.entity, _.insurance)
            res.append((_.id, name))
        return res

    @api.onchange('partner_id')
    def _on_change_entity(self):
        self.entity = self.partner_id.display_name

    def write(self,values):
        employeers_to_remove_origin = self._origin.employeer_ids
        result = super(EpsManagement, self).write(values)
        if 'employeer_ids' in values and not getattr(self, '_writing_employees', False):
            self._writing_employees = True
            employees_to_add = self.mapped('employeer_ids')
            employees_to_remove = set(employeers_to_remove_origin.ids) - set(self.employeer_ids.ids)
            for employee in employees_to_add:
                employee.write({'management_eps': self.id, 'exists_eps': True})
            for employee in employees_to_remove:
                removed_employee = self.env['hr.employee'].search([('id', '=', employee)])
                removed_employee.write({'management_eps': False, 'exists_eps': False})
                removed_employee.exists_eps = False
            self._writing_employees = False
        return result


    @api.constrains('employeer_ids', 'star_date', 'finish_date')
    def _check_employee_conflicts(self):
        for insurance in self:
            for employee in insurance.employeer_ids:
                conflicting_insurances_up = self.env['eps.management'].search([
                    ('id', '!=', insurance.id),
                    ('employeer_ids', 'in', employee.id),
                    '|',
                    ('finish_date', '>=', insurance.finish_date),
                    ('finish_date', '>=', insurance.star_date)
                ])
                conflicting_insurances_down=self.env['eps.management'].search([
                    ('id', '!=', insurance.id),
                    ('employeer_ids', 'in', employee.id),
                    '|',
                    ('finish_date', '<=', insurance.finish_date),
                    ('finish_date', '<=', insurance.star_date)
                ])
                if conflicting_insurances_up and conflicting_insurances_down:
                    raise ValidationError(f"El empleado {employee.name} tiene conflictos de fechas con otros seguros.")

class EpsEmployee(models.Model):
    _inherit = 'hr.employee'

    exists_eps = fields.Boolean(
        string='EPS',
        groups="hr.group_hr_user"
    )
    management_eps = fields.Many2one(
        comodel_name='eps.management',
        string='Poliza EPS',
        groups="hr.group_hr_user"
    )

    def update_management_eps_date(self):
        current_date = fields.Date.today()
        eps_existents = self.env['eps.management'].search([
            ('employeer_ids', 'in', self.id),
            ('star_date', '<=', current_date),
            ('finish_date', '>=', current_date)
        ])
        if eps_existents:
            self.management_eps = eps_existents[0].id
            self.exists_eps = True
        else:
            self.exists_eps = False
            self.management_eps = False

    @api.onchange('exists_eps')
    def _onchange_exists_eps(self):
        if not self.exists_eps:
            self.management_eps = False

    @api.model
    def create(self, values):
        employee = super(EpsEmployee, self).create(values)
        if employee.exists_eps and employee.management_eps:
            employee.management_eps.write({'employeer_ids': [(4, employee.id)]})
        return employee

    def write(self,values):
        poliza_bef = self.management_eps
        result = super(EpsEmployee, self).write(values)
        if 'exists_eps' in values and 'management_eps' in values:
            for employee in self:
                if not employee.exists_eps or not employee.management_eps:
                    poliza_bef.write({'employeer_ids': [(3, employee.id)]})
                    employee.management_eps = False
                    employee.exists_eps = False
                elif employee.exists_eps and employee.management_eps:
                    employee.management_eps.write({'employeer_ids': [(4, employee.id)]})
        return result
