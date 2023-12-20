from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    customer_id = fields.Many2one(
        comodel_name='res.partner',
        string='Nueva dirección de entrega'
    )
    deliver_to_third_parties = fields.Boolean(
        string='Entregar a proveedor/comprador a terceros'
    )
    third_parties = fields.Selection(
        [
            ('01', 'Proveedor'),
            ('02', 'Comprador')
        ],
        string='Proveedor/Comprador'
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('partner_id', False) and not vals.get('customer_id', False):
                vals['customer_id'] = vals['partner_id']
        return super(StockPicking, self).create(vals_list)

    @api.onchange('deliver_to_third_parties')
    def onchange_deliver_to_third_parties(self):
        self.customer_id = self.partner_id

    @api.onchange('partner_id')
    def onchange_deliver_partner_id(self):
        if not self.deliver_to_third_parties:
            self.customer_id = self.partner_id
