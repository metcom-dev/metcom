from odoo.tests.common import TransactionCase


class TestReportPayslipCts(TransactionCase):

    def test_get_last_month_with_data(self):
        report = self.env['report.rent_5ta.report_payroll_projection']
        lines = [
            self.env['payroll.projection.line'].create({'january_amount': 1000}),
            self.env['payroll.projection.line'].create({'february_amount': 2000}),
            self.env['payroll.projection.line'].create({'march_amount': 3000})
        ]

        result = report.get_last_month_with_data(lines)
        expected = {'march_amount': True}

        self.assertEqual(result, expected)
        print('---- TEST GET LAST MONTH WITH DATA -------')

    def test_get_calc_line_1(self):
        report = self.env['report.rent_5ta.report_payroll_projection']
        rent_id = self.env['payroll.projection'].create({})
        month = 3  # March

        result = report.get_calc_line_1(month, rent_id)
        expected = 0  # Replace with expected value

        self.assertEqual(result, expected)

        print('---- TEST GET CALC LINE 1 -------')