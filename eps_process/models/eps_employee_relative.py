from odoo import api, fields, models


class EpsEmployeeRelative(models.Model):
    _inherit = "hr.employee.relative"

    percentage_eps = fields.Integer(string='%EPS')
    tax_eps = fields.Integer(string='Imp.EPS')
    payer_eps = fields.Boolean(string='Pagador EPS')
    disability = fields.Boolean(string='Discapacidad')
    max_age = fields.Integer(string='Edad max')
