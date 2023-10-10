from odoo.tests.common import TransactionCase


class TestReportVoucherUtilities(TransactionCase):
    def setUp(self):
        super(TestReportVoucherUtilities, self).setUp()
        self.ReportVoucherUtilities = self.env["report.voucher_utilities.report_payslip_voucher_utilities"]

    def test_get_report_values(self):
        self.ReportVoucherUtilities._get_report_values()
        print('------TEST REPORT VOUCHER UTILITIES OK--------------')
