from odoo import models, fields


class HrWorkEntryType(models.Model):
    _inherit = 'hr.work.entry.type'

    type_inputs_ids = fields.Many2many('type.inputs')

