from odoo import models, api


class ReportVoucherCTS(models.AbstractModel):
    _name = 'report.voucher_utilities.report_payslip_voucher_utilities'
    _description = 'Voucher Utilidades'

    @api.model
    def _get_report_values(self, docids=None, data=None):
        payslips = self.env['hr.payslip'].browse(docids)
        return {
            'doc_ids': docids,
            'docs': payslips,
            'data': data,
            'employer_sign': self.env['hr.employee'].get_employer_sign(),
            'utilities_lines': self._get_utilities_lines(payslips)
        }

    def _get_utilities_lines(self, payslips):
        lines = {}
        utilities_id = self.env['data.utilities'].search([('is_active', '=', True)])
        for payslip in payslips:
            dias_010 = sum(line.number_of_days for line in payslip.worked_days_line_ids.filtered(lambda x: x.code == 'DIAS_010'))
            utl_003_input = sum(line.amount for line in payslip.input_line_ids.filtered(lambda x: x.code == 'UTL_003'))
            utl_004_input = sum(line.amount for line in payslip.input_line_ids.filtered(lambda x: x.code == 'UTL_004'))
            utl_003_rule = sum(line.amount for line in payslip.line_ids.filtered(lambda x: x.code == 'UTL_003'))
            utl_002_rule = sum(line.amount for line in payslip.line_ids.filtered(lambda x: x.code == 'UTL_002'))
            utl_004_rule = sum(line.amount for line in payslip.line_ids.filtered(lambda x: x.code == 'UTL_004'))
            lines.update({payslip.id: {
                'year': utilities_id[0].date_from.strftime('%Y') if utilities_id else '',
                'annual_rent_before_tax': utilities_id[0].annual_rent_before_tax if utilities_id else 0,
                'percent': utilities_id[0].percent if utilities_id else 0,
                'amount': utilities_id[0].amount if utilities_id else 0,
                'nro_days': utilities_id[0].nro_days if utilities_id else 0,
                'total_amount': utilities_id[0].total_amount if utilities_id else 0,
                'factor_days': utilities_id[0].factor_days if utilities_id else 0,
                'factor_amount': utilities_id[0].factor_amount if utilities_id else 0,
                'dias_010': dias_010,
                'utl_003': utl_003_input,
                'result_d1': utl_003_rule,
                'utl_002_rule': utl_002_rule,
                'utl_004_input': utl_004_input,
                'result_d2': utl_004_rule,
                'result_d3': utl_004_rule + utl_003_rule
            }})
        return lines
