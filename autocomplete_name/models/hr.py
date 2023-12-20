from odoo import api, fields, models


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    @api.onchange('firstname', 'lastname', 'secondname')
    def onchange_fullname(self):
        self.name = '{} {} {}'.format(self.firstname or '', self.lastname or '', self.secondname or '')