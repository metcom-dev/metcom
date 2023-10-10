from odoo import _, fields, models
import requests
import json
from json.decoder import JSONDecodeError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    sync_status_picking = fields.Selection(
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

    def no_report_stock_picking(self):
        for rec in self:
            if rec.sync_status_picking == 'blocked':
                rec.sync_status_picking = 'normal'

    def action_sync_tinka_stock_picking(self):
        """Save Movement with api and change the status sync"""
        token = self.env['res.config.settings'].action_api_intralot()
        url = 'https://api.intrainventario.pe:4431/api/public/asset/savemovement'
        for rec in self:
            if rec.sync_status_picking not in ['normal', 'done'] and rec.state == 'done':
                code_origin = self.find_between(rec.location_id.name, '[', ']')
                code_destiny = self.find_between(rec.location_dest_id.name, '[', ']')
                actives = {}
                for index, line in enumerate(rec.move_line_ids_without_package):
                    if line:
                        if line.lot_id:
                            code_active = line.lot_id.name.split('/')[0] if '/' in line.lot_id.name else ''
                            code_active = code_active.replace(" ", "")
                            actives[index] = {
                                "codigoactivo": code_active,
                                "estadoactivo": line.status.code,
                            }
                data = {
                    "token": token,
                    "codigoorigen": code_origin,
                    "codigodestino": code_destiny,
                    "activos": actives
                }
                response = requests.post(url, data=json.dumps(data))
                response = response.content

                try:
                    response = json.loads(response)
                    msg = response.get('mensaje')
                    err = False
                except JSONDecodeError:
                    msg = str(response)
                    err = True
                message = _(f"Guardar Movimiento - Mensaje: {msg}")
                rec.message_post(
                    body=message
                )
                if not err:
                    if response.get("mensaje") == "OK":
                        self.sync_status_picking = 'done'

    def button_validate(self):
        res = super(StockPicking, self).button_validate()
        self.action_sync_tinka_stock_picking()
        return res

    @staticmethod
    def find_between(string, first, last):
        """Find a string between a two characters"""
        try:
            start = string.index(first) + len(first)
            end = string.index(last, start)
            return string[start:end]
        except ValueError:
            return ""
