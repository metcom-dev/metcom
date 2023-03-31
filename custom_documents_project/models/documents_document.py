from odoo import models, fields, api

import logging
log = logging.getLogger(__name__)

class DocumentsDocument(models.Model):
    _inherit = 'documents.document'

