from odoo import models, fields, api


class HrPayrollStructure(models.Model):
    _inherit = 'hr.payroll.structure'

    @api.model
    def _get_additional_certificate(self):
        selection = super(HrPayrollStructure, self)._get_additional_certificate()
        selection += [('cts', 'CTS Liquidación')]
        return selection
