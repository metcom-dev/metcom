from odoo import models


class StockMoveLine(models.Model):
    _name = 'stock.move.line'
    _inherit = ['stock.move.line', 'mail.thread', 'mail.activity.mixin']
