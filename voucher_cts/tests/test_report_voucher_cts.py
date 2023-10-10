from odoo.tests.common import TransactionCase
from datetime import datetime


class TestReportVoucherCTS(TransactionCase):

    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        user_admin = self.env.ref("base.user_admin")
        self.env = self.env(user=user_admin)
        self.ReportVoucherCTS = self.env["report.voucher_cts.report_payslip_voucher_cts"]
        self.HrPayslip = self.env["hr.payslip"]
        self.partner = self.env["res.partner"].create({"name": "John Doe"})

        self.employee = self.env["hr.employee"].create({
            "name": "John Doe",
        })

        self.payslip = self.HrPayslip.create({
            "name": "Payslip 1",
            "employee_id": self.employee.id,
            "date_from": datetime.now().strftime("%Y-%m-01"),
            "date_to": datetime.now().strftime("%Y-%m-%d"),
        })
        print("ReportVoucherCTS SetUp Report OK ...... !!!!")

    def create_bank_account(self):
        bank = self.env["res.bank"].create({
            "name": "Bank 1"
        })
        bank_account = self.env["res.partner.bank"].create({
            "partner_id": self.partner.id,
            "acc_number": "123456789",
            "bank_id": bank.id
        })
        print("ReportVoucherCTS create_bank_account Report OK ...... !!!!")
        return bank_account.id

    def test_get_bank_data_by_employee(self):
        "Check bank data retrieval for an employee"
        result = self.ReportVoucherCTS.get_bank_data_by_employee(self.payslip)
        expected_result = {
            "acc_number": "",
            "bank_name": ""
        }
        self.assertEqual(result, expected_result)

    def test_get_month_day_range(self):
        "Check calculation of month day range"
        result = self.ReportVoucherCTS.get_month_day_range("01/2023")
        expected_result = (
            datetime.strptime("2023-01-01", "%Y-%m-%d").date(),
            datetime.strptime("2023-01-31", "%Y-%m-%d").date()
        )
        self.assertEqual(result, expected_result)
