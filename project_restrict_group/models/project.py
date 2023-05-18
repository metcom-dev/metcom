from odoo import models, fields, api, _

class Project(models.Model):
    _inherit = 'project.project'

    restrict_group_id = fields.Many2one('res.groups', string='Restrict Group')
    privacy_visibility = fields.Selection(selection_add=[('user_group', 'User Group')], ondelete={'user_group': 'set default'})

    def action_create_group(self):
        for rec in self:
            if not rec.restrict_group_id and rec.privacy_visibility == 'user_group':
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
                rec.restrict_group_id = group.id

    @api.model_create_multi
    def create(self, vals_list):
        self = self.with_context(mail_create_nosubscribe=True)
        projects = super().create(vals_list)
        projects.action_create_group()
        return projects
    
    def write(self, vals):
        res = super(Project, self).write(vals)
        res.action_create_group()
        return res