from odoo import api, fields, models


class HrWorkEntryType(models.Model):
    _inherit = 'hr.work.entry.type'

    is_calc_own_rule = fields.Boolean(string='¿Es calculado por su propia regla?')
