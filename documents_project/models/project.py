from odoo import models, fields, api

import logging
log = logging.getLogger(__name__)

class ProjectProject(models.Model):
    _inherit = 'project.project'

    def write(self, vals):
        res = super(ProjectProject, self).write(vals)
        if 'warehouse_id' in vals:
            project_attachment = self.env['project.attachment'].search([('project_id', 'in', self.ids)])
            project_attachment._compute_warehouse_id()
        return res

class ProjectAttachment(models.Model):
    _inherit = 'project.attachment'

    name = fields.Char(string="Nombre", compute='_compute_name', store=True)
    warehouse_id = fields.Many2one(string="Almacén", comodel_name="stock.warehouse", compute='_compute_warehouse_id', store=True)

    @api.depends('project_id')
    def _compute_warehouse_id(self):
        for rec in self:
            rec.warehouse_id = rec.project_id.warehouse_id.id if rec.project_id else None

    @api.depends('project_id', 'type')
    def _compute_name(self):
        for rec in self:
            if rec.image_name:
                rec.name = rec.image_name

    def donwload_file(self):
        for rec in self:
            return {
                'type': 'ir.actions.act_url',
                'url': '/web/content/%s?download=true' % (rec.id),
                'target': 'new',
            }