from odoo import models, fields, api


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    def _default_get_id_user(self):
        return self.env.user

    assign_to = fields.Many2many(
        comodel_name='res.users',
        string='Asignado a',
        groups='add_user_by_journal.group_assign_to',
        default = _default_get_id_user,
    )

    assign_to_domain = fields.Many2many(
        comodel_name='res.users',
        relation='account_journal_res_users_rel_satel',
        string='Asignado a (para el dominio)',
        default=_default_get_id_user,
    )

    @api.onchange('assign_to')
    def _onchange_assing_to_domain(self):
        for rec in self:
            new_users_ids = rec.assign_to_domain - rec.assign_to if len(rec.assign_to) < len(rec.assign_to_domain) else rec.assign_to
            if new_users_ids:
                for user in new_users_ids:
                    user_id = str(user.id).split('_')[-1]
                    if user.has_group('add_user_by_journal.group_assign_to'):
                        if user not in self.assign_to_domain:
                            total_domain = self.assign_to_domain + user
                            self.assign_to_domain = total_domain
                        elif user in self.assign_to_domain and user not in self.assign_to and user_id != str(self._default_get_id_user().id):
                            total_domain = self.assign_to_domain - user
                            self.assign_to_domain = total_domain

                    else:
                        if user in self.assign_to_domain and user not in self.assign_to:
                            total_domain = self.assign_to_domain - user
                            self.assign_to_domain = total_domain


class ResUsers(models.Model):
    _inherit = 'res.users'

    def write(self, vals):
        res = super(ResUsers, self).write(vals)
        for user in self:
            if user.has_group('add_user_by_journal.group_assign_to'):
                journals = self.env['account.journal'].search([])
                for journal in journals:
                    if user not in journal.assign_to_domain:
                        total_domain = journal.assign_to_domain + user
                        journal.assign_to_domain = total_domain
            else:
                journals = self.env['account.journal'].search([])
                for journal in journals:
                    if user in journal.assign_to_domain and user not in journal.sudo().assign_to:
                        total_domain = journal.assign_to_domain - user
                        journal.assign_to_domain = total_domain
        return res

