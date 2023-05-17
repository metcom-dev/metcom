from odoo import api, fields, models


class HrContract(models.Model):

    _inherit = 'hr.contract'

    reason_low_id = fields.Many2one(
        comodel_name='low.reason',
        string='Motivo de baja'
    )
    mintra_contract_id = fields.Many2one(
        comodel_name='mintra.contract',
        string='Tipo de Contrato'
    )
    compensation_in_kind = fields.Boolean(
        string=u'Remuneración en especie'
    )
