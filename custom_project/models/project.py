from odoo import models, fields, api

import logging
log = logging.getLogger(__name__)

class Project(models.Model):
    _inherit = 'project.project'

    requirement_ids = fields.One2many(string='Requerimientos', comodel_name='purchase.preorder', inverse_name='project_id', copy=True, readonly=True)
    purchase_attachs_ids = fields.One2many(
        string='Ordenes de Compra',
        comodel_name='project.attachment',
        inverse_name='project_id',
        domain=[('type', '=', 'purchase')],
        copy=True
    )
    photo_attachs_ids = fields.One2many(
        string='Informes y Fotografias',
        comodel_name='project.attachment',
        inverse_name='project_id',
        domain=[('type', '=', 'photo')],
        copy=True
    )
    other_attachs_ids = fields.One2many(
        string='Otros',
        comodel_name='project.attachment',
        inverse_name='project_id',
        domain=[('type', '=', 'other')],
        copy=True
    )
    warehouse_id = fields.Many2one(string="Almacén", comodel_name="stock.warehouse")

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'El nombre del proyecto debe ser unico.'),
    ]

    def go_principal_panel(self):
        for rec in self:
            return {
                'name': 'Proyecto',
                'view_mode': 'form',
                'view_type': 'form',
                'view_id': self.env.ref('project.edit_project').id,
                'res_model': 'project.project',
                'res_id': rec.id,
                'type': 'ir.actions.act_window',
                'target': 'current',
                'domain': ""
            }

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            sequence = self.env['ir.sequence'].next_by_code('project.project_project_sequence')
            vals['name'] = sequence + vals['name']
            if 'warehouse_id' not in vals:
                vals['warehouse_id'] = self.env.user.property_warehouse_id.id if self.env.user.property_warehouse_id else None
        res = super(Project, self).create(vals)
        return res
    
    @api.model
    def web_search_read(self, domain=None, fields=None, offset=0, limit=None, order=None, count_limit=None):
        if 'warehouse_id' not in fields:
            fields.append('warehouse_id')
        warehouse_id = self.env.user.property_warehouse_id.id if self.env.user.property_warehouse_id else None
        if warehouse_id:
            domain.append('|')
            domain.append(['warehouse_id', '=', warehouse_id])
            domain.append(['warehouse_id', '=', False])
        res = super(Project, self).web_search_read(domain=domain, fields=fields, offset=offset, limit=limit, order=order, count_limit=count_limit)
        return res

class ProjectAttachment(models.Model):
    _name = 'project.attachment'
    _description = 'Lineas de Mano de Obra de Proyecto'

    project_id = fields.Many2one(string='Proyecto', comodel_name='project.project', ondelete='cascade')
    image = fields.Binary(string="Archivo", required=True)
    image_name = fields.Char(string="Nombre Archivo")
    type = fields.Selection(string='Tipo', selection=[
        ('purchase', 'Compras'), 
        ('photo', 'Fotos e Informes'),
        ('other', 'Otros'),
    ], required=True)