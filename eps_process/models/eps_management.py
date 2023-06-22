from odoo import models, fields, api


class EpsManagement(models.Model):
    _name = "eps.management"
    _description = "EPS management"

    star_date = fields.Date(string='Fecha de inicio', required=True)
    finish_date = fields.Date(string='Fecha de finalización', required=True)
    entity = fields.Char(string='Entidad', required=True)
    insurance = fields.Char(string='N° de poliza')
    rate_employer = fields.Float(string='Tasa')
    amount_employer = fields.Float(string='Importe')
    rate_worker = fields.Float(string='Tasa')
    amount_worker = fields.Float(string='Importe')
    employeer_ids = fields.One2many(
        'hr.employee', 'management_eps', string='Empleados')

    def name_get(self):
        res = []
        for _ in self:
            name = "%s-%s" % (_.entity, _.insurance)
            res.append((_.id, name))
        return res


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
