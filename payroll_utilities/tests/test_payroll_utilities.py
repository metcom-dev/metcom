from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError

class TestDataUtilities(TransactionCase):

    def test_compute_fields(self):
        data_util = self.env['data.utilities'].create({
            'date_from': '2023-01-01',
            'date_to': '2023-12-31',
            'annual_rent_before_tax': 10000,
            'percent': 0.5,
            'is_active': True
        })

        data_util.compute_fields()
        print('------TEST COMPUTE PAYROLL UTILITIES OK--------------')

    def test_check_is_active(self):
        data_util1 = self.env['data.utilities'].create({
            'date_from': '2023-01-01',
            'date_to': '2023-12-31',
            'annual_rent_before_tax': 10000,
            'percent': 0.5,
            'is_active': True
        })
        with self.assertRaises(ValidationError):
            data_util2 = self.env['data.utilities'].create({
                'date_from': '2023-01-01',
                'date_to': '2023-12-31',
                'annual_rent_before_tax': 20000,
                'percent': 0.8,
                'is_active': True
            })
        print('------TEST CHECK PAYROLL UTILITIES OK--------------')