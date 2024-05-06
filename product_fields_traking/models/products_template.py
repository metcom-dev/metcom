from odoo import models, fields, api, _
import logging
log = logging.getLogger(__name__)

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    list_price = fields.Float(tracking=True)
    standard_price = fields.Float(tracking=True)

    uom_id = fields.Many2one(tracking=True)

    @api.model
    def create(self, vals):
        record = super(ProductTemplate, self).create(vals)
        record.track_multi_uom_changes(vals)
        return record

    def track_multi_uom_changes(self, vals):
        pass

    def write(self, vals):
        self.track_multi_uom_changes(vals)
        return super(ProductTemplate, self).write(vals)


