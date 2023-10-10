from odoo import _, fields, models
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare
import requests
import json


class StockQuant(models.Model):
    _inherit = "stock.quant"

    sync_status_inventory = fields.Selection(
        selection=[
            ('normal', 'No Informar'),
            ('done', 'Sincronizado a Intralot'),
            ('blocked', 'No Sincronizado'),
        ],
        string='Sync status',
        default='blocked',
        tracking=True,
        copy=False
    )

    def no_report_stock_inventory(self):
        for rec in self:
            if rec.sync_status_inventory == 'blocked':
                rec.sync_status_inventory = 'normal'

    def action_sync_tinka_stock_inventory(self):
        """Save Inventory with api and change the status sync"""
        token = self.env['res.config.settings'].action_api_intralot()
        url = 'https://api.intrainventario.pe:4431/api/public/asset/saveinventory'
        status = 'done'
        for rec in self:
            if rec.sync_status_inventory not in ['normal', 'done']:
                code_origin = ''
                actives = {}
                if rec.location_id.name:
                    code_origin = self.find_between(rec.location_id.name, '[', ']')
                    break
                if rec.lot_id:
                    code_active = rec.lot_id.name.split('/')[0] if '/' in rec.lot_id.name else ''
                    code_active = code_active.replace(" ", "")
                    actives[0] = {
                        "codigoactivo": code_active,
                        "estadoactivo": status,
                    }
                else:
                    actives[0] = {
                        "codigoactivo": '1',
                        "estadoactivo": status,
                    }
                data = {
                    "token": token,
                    "codigoorigen": code_origin,
                    "activos": actives
                }                  
                response = requests.post(url, data=json.dumps(data))
                response = response.content
                response = json.loads(response)
                if response.get("mensaje") == "OK":
                    rec.sync_status_inventory = 'done'

    def _apply_inventory(self):
        move_vals = []
        if not self.user_has_groups('stock.group_stock_manager'):
            raise UserError(_('Only a stock manager can validate an inventory adjustment.'))
        for quant in self:
            # Create and validate a move so that the quant matches its `inventory_quantity`.
            if float_compare(quant.inventory_diff_quantity, 0, precision_rounding=quant.product_uom_id.rounding) > 0:
                move_vals.append(
                    quant._get_inventory_move_values(quant.inventory_diff_quantity,
                                                     quant.product_id.with_company(quant.company_id).property_stock_inventory,
                                                     quant.location_id))
            else:
                move_vals.append(
                    quant._get_inventory_move_values(-quant.inventory_diff_quantity,
                                                     quant.location_id,
                                                     quant.product_id.with_company(quant.company_id).property_stock_inventory,
                                                     out=True))
        moves = self.env['stock.move'].with_context(inventory_mode=False).create(move_vals)
        moves._action_done()
        
        for rec in moves.move_line_ids:
            message = _(f"Guardar Inventario - Mensaje: OK")
            rec.message_post(
                body=message
            )
        
        self.location_id.write({'last_inventory_date': fields.Date.today()})
        date_by_location = {loc: loc._get_next_inventory_date() for loc in self.mapped('location_id')}
        for quant in self:
            quant.inventory_date = date_by_location[quant.location_id]
        self.write({'inventory_quantity': 0, 'user_id': False})
        self.write({'inventory_diff_quantity': 0})

    
    def action_apply_inventory(self):
        super(StockQuant, self).action_apply_inventory()
        self.action_sync_tinka_stock_inventory()
    
    @staticmethod
    def find_between(string, first, last):
        """Find a string between a two characters"""
        try:
            start = string.index(first) + len(first)
            end = string.index(last, start)
            return string[start:end]
        except ValueError:
            return ""
