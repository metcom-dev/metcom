from odoo import models, fields, api, _

class Project(models.Model):
    _inherit = 'project.project'

    restrict_group_id = fields.Many2one('res.groups', string='Restrict Group')

    def action_create_group(self):
        if not self.restrict_group_id:
            group = self.env['res.groups'].create({
                'name': 'Project %s ' % self.name,
                'users': [(6, 0, [self.user_id.id])],
                'rule_groups':[(0, 0, {
                    'name':'Project %s ' % self.name,
                    'model_id':self.env['ir.model'].search([('model','=','project.project')]).id,
                    'domain_force':"[('id','=',%s)]" % self.id,
                    'perm_read':True,
                    'perm_write':True,
                    'perm_create':True,
                    'perm_unlink':True,
                })]
            })
            self.restrict_group_id = group.id

    def create(self, vals):
        res = super(Project, self).create(vals)
        res.action_create_group()