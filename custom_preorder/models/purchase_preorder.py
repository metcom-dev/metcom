from odoo import models, fields, api

import logging
log = logging.getLogger(__name__)

class PrePurchase(models.Model):
    _inherit = 'purchase.preorder'

    po_state = fields.Selection([
        ("pending", "Pendiente"),
        ("w_stock", "Stock Disponible"),
        ("generate", "Atendido"),
    ], string='Estado OC', default="pending", compute="_compute_po_state", store=True, copy=False)

    @api.depends("check_po_generated")
    def _compute_po_state(self):
        for preorder_id in self:
            preorder_id.po_state = "generate" if preorder_id.check_po_generated else "pending"