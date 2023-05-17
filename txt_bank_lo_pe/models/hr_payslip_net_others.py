from odoo import api, fields, models


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    net_other = fields.Monetary(string='Neto', compute='_compute_other_net')

    def _compute_other_net(self):
        for payslip in self:
            payslip.net_other = payslip._get_salary_line_other_net('Neto')

    def _get_salary_line_other_net(self,code):
        lines = self.line_ids.filtered(lambda line: line.category_id.name == code)
        return sum([line.total for line in lines])