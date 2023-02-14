from odoo import models, fields

class PrePurchase(models.Model):
    _inherit = 'purchase.preorder'

    check_po_generated = fields.Boolean(
        string='PO generado por cron',
        default=False,
    )