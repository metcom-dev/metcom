from odoo import fields, api, models, _

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    carrier_id = fields.Many2one('res.partner', string='Transportista', domain=[('is_carrier', '=', True)])