from odoo.tests.common import TransactionCase


class TestPayrollProjection(TransactionCase):
    
    def setUp(self):
        super().setUp()
        self.PayrollProjection = self.env['payroll.projection']

    def test_create_payroll_projection(self):
        projection = self.PayrollProjection.create({})
        self.assertTrue(projection)
        print('---- TEST CREATE PAYROLL PROJECTION ------')

    def test_line_ids_amounts(self):
        projection = self.PayrollProjection.create({})
        line_ids = projection._get_line_ids()
        amount_keys = ['january_amount', 'february_amount', 'march_amount', 'april_amount', 'may_amount',
                       'june_amount', 'july_amount', 'august_amount', 'september_amount', 'october_amount',
                       'november_amount', 'december_amount']
        for line in line_ids:
            for key in amount_keys:
                if key in line[2]:
                    self.assertIsNotNone(line[2][key])
        print('---- TEST LINE IDS AMOUNTS ------')