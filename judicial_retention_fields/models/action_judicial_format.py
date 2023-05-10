from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    def action_get_judicial_format(self):
        ids = self.mapped('id')
        if not ids:
            raise ValidationError(u'No hay registros seleccionados.')
        action_name = "judicial_retention_fields.report_judicial_format_hr_payslip"
        return self.env.ref(action_name).report_action(self)

    def _get_paid_amount_judicial(self):
        self.ensure_one()
        if not self.worked_days_line_ids:
            return self._get_contract_wage()
        return sum([line.amount if line.code in ["DJF_001", "DJP_002"] else 0.00 for line in self.line_ids])

    def _uppercase_beneficiary_name(self):
        beneficiary_name = self.employee_id.beneficiary.name
        employee_beneficiary_name = beneficiary_name.upper()
        return employee_beneficiary_name

    def _uppercase_employee_id_name(self):
        employee_name = self.employee_id.name
        employee_id_name = employee_name.upper()
        return employee_id_name
