from odoo import api, models


class ReportAdditionalPayslip(models.AbstractModel):
    _name = 'report.setting_voucher.template_additional_report_hr_payslip'
    _description = 'Payslip Additional Report'

    @api.model
    def _get_report_values(self, docids=None, data=None):
        payslips = self.env['hr.payslip'].browse(docids)
        employer_sign = self.env['hr.employee'].get_employer_sign()
        return {
            'doc_ids': docids,
            'docs': payslips,
            'data': data,
            'doc_model': 'hr.payslip',
            'employer_sign': employer_sign
        }
