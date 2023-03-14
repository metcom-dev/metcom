from odoo import models, fields, api

class Users(models.Model):
    _inherit = 'res.users'

    property_warehouse_ids= fields.Many2many('stock.warehouse', string='Almacenes')
