from datetime import date
from odoo.tests.common import TransactionCase

class TestRatesFifthRent(TransactionCase):

    def setUp(self):
        super().setUp()

        self.uit_data = self.env['various.data.uit'].create({
            'is_active': True,
            'uit_amount': 100.0,
        })

    def test_rates_fifth_rent(self):
        rent = self.env['rates.fifth_rent'].create({
            'date_from': '2023-01-01',
            'date_to': '2023-12-31',
        })

        self.assertEqual(rent.date_from, date.fromisoformat('2023-01-01'))
        self.assertEqual(rent.date_to, date.fromisoformat('2023-12-31'))

        rent.write({
            'date_from': '2023-02-01',
            'date_to': '2023-11-30',
        })

        self.assertEqual(rent.date_from, date.fromisoformat('2023-02-01'))
        self.assertEqual(rent.date_to, date.fromisoformat('2023-11-30'))
        print('--------- TEST RATES FIFTH RENT --------------')

    def test_rates_fifth_rent_line(self):
        rent = self.env['rates.fifth_rent'].create({
            'date_from': '2023-01-01',
            'date_to': '2023-12-31',
        })

        rent_line = self.env['rates.fifth_rent.line'].create({
            'sequence': 1,
            'rate_parent_id': rent.id,
            'name': 'Tramo 1',
            'value_from': 0,
            'value_to': 1000,
            'percent': 10.0,
        })

        self.assertEqual(rent_line.sequence, 1)
        self.assertEqual(rent_line.name, 'Tramo 1')
        self.assertEqual(rent_line.value_from, 0)
        self.assertEqual(rent_line.value_to, 1000)
        self.assertEqual(rent_line.percent, 10.0)

        rent_line.write({
            'name': 'Tramo 2',
            'percent': 15.0,
        })

        self.assertEqual(rent_line.name, 'Tramo 2')
        self.assertEqual(rent_line.percent, 15.0)

        updated_values = rent_line.set_amount_per_record({
            'value_from': 500,
            'value_to': 800,
        })
        self.assertEqual(updated_values['amount_from'], 50000.0)
        self.assertEqual(updated_values['amount_to'], 80000.0)
        print('--------- TEST RATES FIFTH RENT LINE --------------')