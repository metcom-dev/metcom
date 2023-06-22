from odoo import api, fields, models


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    fl_from = fields.Float(string='Desde')
    fl_to = fields.Float(string='Hasta')

    @api.onchange('fl_from', 'fl_to')
    def _onchange_unit_amount(self):
        if self.fl_from < self.fl_to:
            self.unit_amount = self.fl_to - self.fl_from
