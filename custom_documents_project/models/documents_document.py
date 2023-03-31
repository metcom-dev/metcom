from odoo import models, fields, api

import logging
log = logging.getLogger(__name__)

class DocumentsDocument(models.Model):
    _inherit = 'documents.document'

    project_id = fields.Many2one(string="Proyecto", comodel_name="project.project", compute='_compute_project_id', store=True)
    warehouse_id = fields.Many2one(string="Almacen", comodel_name="stock.warehouse")

    @api.depends('attachment_id', 'attachment_id.res_model', 'attachment_id.res_id')
    def _compute_project_id(self):
        for rec in self:
            log.info(res.attachment_name)
            log.info(rec.res_model)
            log.info(rec.res_id)

