from odoo import models, fields, api

import logging
log = logging.getLogger(__name__)

class DocumentsDocument(models.Model):
    _inherit = 'documents.document'

    def download_file_metcom(self):
        for rec in self:
            return {
                'type': 'ir.actions.act_url',
                'url': '/web/content/%s?download=true' % (rec.attachment_id.id),
                'target': 'new',
            }