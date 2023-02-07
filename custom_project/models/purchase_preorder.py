from odoo import models, fields

class PrePurchase(models.Model):
    _inherit = 'purchase.preorder'

    project_id = fields.Many2one(string="Proyecto", comodel_name="project.project")