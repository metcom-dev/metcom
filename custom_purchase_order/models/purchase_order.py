from odoo import models, fields, api

import logging
log = logging.getLogger(__name__)

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'