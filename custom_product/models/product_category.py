from odoo import models, fields

class ProductCategory(models.Model):
    _inherit = 'product.category'

    # supplier_one = fields.Many2one('res.partner', string='Proveedor 1')
    # supplier_two = fields.Many2one('res.partner', string='Proveedor 2')
    # supplier_three = fields.Many2one('res.partner', string='Proveedor 3')

    supplier_ids = fields.Many2many(string='Proveedores', comodel_name='res.partner')