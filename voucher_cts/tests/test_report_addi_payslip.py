from odoo.tests.common import TransactionCase
from datetime import datetime
# from dateutil.relativedelta import relativedelta

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


class TestReportAdditionalPayslip(TransactionCase):

    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        user_admin = self.env.ref("base.user_admin")
        self.env = self.env(user=user_admin)
        self.ReportAdditionalPayslip = self.env["report.setting_voucher.template_additional_report_hr_payslip"]
        self.HrPayslip = self.env["hr.payslip"]
        print("ReportAdditionalPayslip SetUp Report OK ...... !!!!")

    def test_get_actual_formatted_date(self):
        "Check actual formatted date"
        today = datetime.today()
        month_name = dict(months).get(str(today.month))
        expected_date = "{} de {} del {}".format(
            today.day, month_name, today.year)
        formatted_date = self.ReportAdditionalPayslip.get_actual_formatted_date()
        self.assertEqual(formatted_date, expected_date)
        print(
            "ReportAdditionalPayslip test get_actual_formatted_date Report OK ...... !!!!")

    def test_get_payslip_data_cts(self):
        "Check payslip data for CTS"
        employee = self.env["hr.employee"].create({"name": "John Doe"})
        partner = self.env["res.partner"].create({"name": "John Doe"})
        bank = self.env["res.bank"].create({"name": "Bank 1"})
        bank_account = self.env["res.partner.bank"].create({
            "partner_id": partner.id,
            "acc_number": "123456789",
            "bank_id": bank.id
        })
        employee.bank_account_id = bank_account.id
        payslip = self.HrPayslip.create(
            {"name": "Payslip 1", "employee_id": employee.id})
        report = self.env["report.setting_voucher.template_additional_report_hr_payslip"]
        payslip_data = report.get_payslip_data_cts(
            self.env["hr.payslip"].browse(payslip.id))
        expected_payslip_data = {payslip.id: {
            "acc_number": "123456789", "bank_name": "BANK 1"}}
        self.assertEqual(payslip_data, expected_payslip_data)
        print("ReportAdditionalPayslip test get_payslip_data_cts Report OK ...... !!!!")
