from odoo import fields, api, models, _
from odoo.exceptions import UserError

import logging
log = logging.getLogger(__name__)

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    carrier_id = fields.Many2one('res.partner', string='Transportista', domain=[('is_carrier', '=', True)])
    bank_type = fields.Many2one('res.bank', string='Banco')
    partner_banks = fields.One2many(related='partner_id.bank_ids', readonly=True)
    allowed_bank_type_ids = fields.Many2many(
        'res.bank', compute='_compute_allowed_bank_type_ids'
    )

    def button_unlock(self):
        if not self.env.user.has_group('custom_order_print.group_logistic_security'):
            raise UserError("No tiene permisos para desbloquear la orden de compra")
        res = super(PurchaseOrder, self).button_unlock()
        return res

    @api.depends('partner_id')
    def _compute_allowed_bank_type_ids(self):
        for order in self:
            bank_type_ids = []
            if order.partner_id.bank_ids:
                for bank in order.partner_id.bank_ids:
                    if bank.bank_id.id not in bank_type_ids:
                        bank_type_ids.append(bank.bank_id.id)
            order.allowed_bank_type_ids = self.env['res.bank'].browse(bank_type_ids)

    