from odoo import models, fields, api

import logging
log = logging.getLogger(__name__)

class PrePurchase(models.Model):
    _inherit = 'purchase.preorder'