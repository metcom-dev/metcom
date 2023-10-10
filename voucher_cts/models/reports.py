import datetime
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api

months = [
    ('1', 'Enero'),
    ('2', 'Febrero'),
    ('3', 'Marzo'),
    ('4', 'Abril'),
    ('5', 'Mayo'),
    ('6', 'Junio'),
    ('7', 'Julio'),
    ('8', 'Agosto'),
    ('9', 'Setiembre'),
    ('10', 'Octubre'),
    ('11', 'Noviembre'),
    ('12', 'Diciembre')
]


class ReportAdditionalPayslip(models.AbstractModel):
    _inherit = 'report.setting_voucher.template_additional_report_hr_payslip'

    @api.model
    def _get_report_values(self, docids=None, data=None):
        r = super(ReportAdditionalPayslip,
                  self)._get_report_values(docids, data)
        payslips = self.env['hr.payslip'].browse(docids)
        r['formatted_date'] = self.get_actual_formatted_date()
        r['payslip_data'] = self.get_payslip_data_cts(payslips)
        return r

    @staticmethod
    def get_actual_formatted_date():
        today = fields.Date.today()
        year = today.year
        month = today.month
        day = today.day
        formatted_date = '{} de {} del {}'.format(
            day, months[month - 1][1], year)
        return formatted_date

    @staticmethod
    def get_payslip_data_cts(payslips):
        lines = {}
        for payslip in payslips:
            acc_number = ''
            bank_name = ''
            if payslip.employee_id.bank_account_id:
                bank_account_id = payslip.employee_id.bank_account_id
                acc_number = bank_account_id.acc_number
                bank_name = bank_account_id.bank_id.name.upper() if bank_account_id.bank_id else ''
            lines.update({payslip.id: {
                'acc_number': acc_number,
                'bank_name': bank_name
            }})
        return lines


class ReportVoucherCTS(models.AbstractModel):
    _name = 'report.voucher_cts.report_payslip_voucher_cts'
    _description = 'Voucher CTS'

    @api.model
    def _get_report_values(self, docids=None, data=None):
        payslips = self.env['hr.payslip'].browse(docids)
        return {
            'doc_ids': docids,
            'docs': payslips,
            'data': data,
            'employer_sign': self.env['hr.employee'].get_employer_sign(),
            'periods': self._get_periods(payslips),
            'get_lines': self.get_lines_cts_filtered,
            'get_bank_data_by_employee': self.get_bank_data_by_employee
        }

    @staticmethod
    def get_bank_data_by_employee(payslip):
        acc_number = ''
        bank_name = ''
        if payslip.employee_id.bank_account_id:
            bank_account_id = payslip.employee_id.bank_account_id
            acc_number = bank_account_id.acc_number
            bank_name = bank_account_id.bank_id.name.upper() if bank_account_id.bank_id else ''
        return {
            'acc_number': acc_number,
            'bank_name': bank_name
        }

    def get_lines_cts_filtered(self, line_ids):
        category_id = self.env.ref(
            'basic_rule.hr_salary_rule_category_bcb_001', False)
        lines = line_ids.filtered(
            lambda x: x.category_id == category_id and x.amount > 0)
        return lines

    @staticmethod
    def get_month_day_range(period):
        datetime_str = '{}-{}-01 15:00:00'.format(period[3:], period[0:2])
        datetime_object = datetime.datetime.strptime(
            datetime_str, '%Y-%m-%d %H:%M:%S').date()
        last_day = datetime_object + relativedelta(day=1, months=+1, days=-1)
        first_day = datetime_object + relativedelta(day=1)
        return first_day, last_day

    def _get_periods(self, payslips):
        lines = {}
        for payslip in payslips:
            if int(payslip.month) in [12, 1, 2, 3, 4, 5]:
                first_day, _ = self.get_month_day_range(
                    '11/' + str(int(payslip.year) - 1))
            else:
                first_day, _ = self.get_month_day_range('05/' + payslip.year)
            date_start = payslip.date_start_dt - relativedelta(months=1)
            _, last_day = self.get_month_day_range(
                date_start.strftime('%m/%Y'))
            lines.update({payslip.id: {
                'date_from': first_day,
                'date_to': last_day,
            }})
        return lines
