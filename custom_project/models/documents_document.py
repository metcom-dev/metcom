from odoo import models, fields

import logging
log = logging.getLogger(__name__)

class Document(models.Model):
    _inherit = 'documents.document'

    project_id = fields.Many2one(string='Proyecto', comodel_name='project.project', ondelete='cascade')
    warehouse_id = fields.Many2one(string="Almacen", comodel_name='stock.warehouse', related="project_id.warehouse_id", store=True, ondelete='cascade')

    def create(self, vals):
        res = super(Document, self).create(vals)
        if res.project_id:
            body = f"Subió a la carpeta {res.folder_id.name} el archivo {res.name}."
            res.project_id.message_post(body=body)
        return res