from odoo import models, fields

class ProductCategory(models.Model):
    _inherit = 'product.category'

    supplier_ids = fields.Many2many(string='Proveedores', comodel_name='res.partner')