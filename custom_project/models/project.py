from odoo import models, fields, api

import logging
log = logging.getLogger(__name__)

class Project(models.Model):
    _inherit = 'project.project'

    requirement_ids = fields.One2many(string='Requerimientos', comodel_name='purchase.preorder', inverse_name='project_id', copy=True, readonly=True)
    warehouse_id = fields.Many2one(string="Almacén", comodel_name="stock.warehouse")
    purchase_folder_id = fields.Many2one(string='Carpeta de Compras', comodel_name='documents.folder')
    photo_folder_id = fields.Many2one(string='Carpeta de Fotos', comodel_name='documents.folder')
    other_folder_id = fields.Many2one(string='Carpeta de Otros', comodel_name='documents.folder')
    purchase_attachs_ids = fields.One2many(
        string='Ordenes de Compra',
        comodel_name='documents.document',
        inverse_name='project_id',
        domain=lambda self: [('folder_id', '=', self.purchase_folder_id.id)],
        copy=True
    )
    photo_attachs_ids = fields.One2many(
        string='Informes y Fotografias',
        comodel_name='documents.document',
        inverse_name='project_id',
        domain=lambda self: [('folder_id', '=', self.photo_folder_id.id)],
        copy=True
    )
    other_attachs_ids = fields.One2many(
        string='Otros',
        comodel_name='documents.document',
        inverse_name='project_id',
        domain=lambda self: [('folder_id', '=', self.other_folder_id.id)],
        copy=True
    )

    analytic_account_id = fields.Many2one('account.analytic.account', string="Analytic Account", copy=False, ondelete='set null',
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]", check_company=True,
        help="Analytic account to which this project, its tasks and its timesheets are linked. \n"
            "Track the costs and revenues of your project by setting this analytic account on your related documents (e.g. sales orders, invoices, purchase orders, vendor bills, expenses etc.).\n"
            "This analytic account can be changed on each task individually if necessary.\n"
            "An analytic account is required in order to use timesheets.", tracking=True)
    
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
            if 'warehouse_id' not in vals or not vals['warehouse_id']:
                vals['warehouse_id'] = self.env.user.property_warehouse_ids[0].id if self.env.user.property_warehouse_ids else None
            if "sale_line_id" in vals and vals["sale_line_id"]:
                self.env.context = dict(self.env.context)
                self.env.context.update({"no_create_folder": False})
        res = super(Project, self).create(vals_list)
        for project_id in res:
            if project_id.documents_folder_id:
                folder_data = {"name": 'Compras', "parent_folder_id": project_id.documents_folder_id.id, "company_id": self.env.user.company_id.id}
                project_id.purchase_folder_id = self.env["documents.folder"].create(folder_data).id

                folder_data.update({"name": "Informes y fotografías"})
                project_id.photo_folder_id = self.env["documents.folder"].create(folder_data).id

                folder_data.update({"name": "Otros"})
                project_id.other_folder_id = self.env["documents.folder"].create(folder_data).id
        return res

    def write(self, vals):
        if 'name' in vals:
            folder_id = self.env["documents.folder"].search([('name', '=', self.name)])
            folder_id.write({"name": vals['name']})
        return super(Project, self).write(vals)