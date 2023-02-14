from odoo import models, fields, api

import logging
log = logging.getLogger(__name__)

class Project(models.Model):
    _inherit = 'project.project'

    requirement_ids = fields.One2many(string='Requerimientos', comodel_name='purchase.preorder', inverse_name='project_id', copy=True, readonly=True)
    labor_ids = fields.One2many(string='Mano de Obra', comodel_name='project.labor', inverse_name='project_id', copy=True)
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
            vals['name'] = sequence[:-1] + vals['name']
        res = super(Project, self).create(vals)
        return res

class ProjectLabor(models.Model):
    _name = 'project.labor'
    _description = 'Lineas de Mano de Obra de Proyecto'

    project_id = fields.Many2one(string='Proyecto', comodel_name='project.project', ondelete='cascade')
    employee_id = fields.Many2one(string="Empleado", comodel_name='hr.employee', ondelete='restrict', required=True)
    employee_vat = fields.Char(string="DNI")
    hours = fields.Float(string="Horas Dedicadas", required=True)

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        if not self.employee_id:
            return
        self.employee_vat = self.employee_id.identification_id

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