from odoo import models, fields, api, _

class Project(models.Model):
    _inherit = 'project.project'

    restrict_group_id = fields.Many2one('res.groups', string='Restrict Group')
    backup_restrict_group_id = fields.Many2one('res.groups', string='Restrict Group (Back-up)')
    privacy_visibility = fields.Selection(selection_add=[('user_group', 'User Group')], ondelete={'user_group': 'set default'})

    def action_create_group(self):
        for rec in self:
            if not rec.restrict_group_id and rec.privacy_visibility == 'user_group':
                if not rec.backup_restrict_group_id:
                    group = self.env['res.groups'].create({
                        'name': _('Project %s ' % self.name),
                        'users': [(6, 0, [self.user_id.id])]
                    })
                else:
                    group = rec.backup_restrict_group_id
                rec.with_context(called_from_action_create_group=True).write({
                    'restrict_group_id': group.id,
                    'backup_restrict_group_id': group.id,
                })

    @api.model_create_multi
    def create(self, vals_list):
        self = self.with_context(mail_create_nosubscribe=True)
        projects = super().create(vals_list)
        projects.action_create_group()
        return projects
    
    def write(self, vals):
        res = super(Project, self).write(vals)
        if self._context.get('called_from_action_create_group', False):
            return res
        self.action_create_group()
        return res
    
    @api.onchange('privacy_visibility')
    def _onchange_privacy_visibility_restrict(self):
        if self.privacy_visibility!='user_group':
            self.restrict_group_id = False