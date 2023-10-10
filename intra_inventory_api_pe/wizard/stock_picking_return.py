from odoo import models


class ReturnPicking(models.TransientModel):
    _inherit = 'stock.return.picking'

    def _create_returns(self):
        res = super(ReturnPicking, self)._create_returns()
        new_picking_id, pick_type_id = res
        new_picking_id = self.env['stock.picking'].search([('id','=',new_picking_id)])
        new_picking_id.write({'sync_status_picking':'blocked'}) if new_picking_id else False
        return res