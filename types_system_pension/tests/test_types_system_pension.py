from odoo.tests import Form
from odoo.addons.hr.tests.common import TestHrCommon
from datetime import datetime


class TestHrEmployee(TestHrCommon):

    def setUp(self):
        super().setUp()
        tope_afp = self.env['tope.afp'].create({
            'date_from': datetime(2021, 1, 4),
            'date_to': datetime(2021, 1, 5),
            'top': 4
        })
        pension_system = self.env['pension.system'].create({
            'code': 'code prueba',
            'pension_system': 'regimen prueba',
            'name': 'abreviatura',
            'private_sector': True,
            'public_sector': True,
            'other_entities': True,
            'cuspp': True,
            'comis_pension_ids': False
        })
        comis_pension = self.env['comis.system.pension'].create({
            'date_from': datetime(2021, 1, 4),
            'date_to': datetime(2021, 1, 5),
            'fund': 4,
            'bonus': 5,
            'mixed_flow': 7,
            'flow': 8,
            'balance': 9,
            'pension_id': pension_system.id
        })

        self.user_without_image = self.env['res.users'].create({
            'name': 'Marc Demo',
            'email': 'mark.brown23@example.com',
            'image_1920': False,
            'login': 'demo_1',
            'password': 'demo_123'
        })
        self.employee_without_image = self.env['hr.employee'].create({
            'user_id': self.user_without_image.id,
            'image_1920': False,
            'cuspp': 'cuspp 2',
            'is_cuspp': True,
            'pension_system_id': pension_system.id,
            'pension_sctr': True,
            'commission_type': 'amount'
        })

    def test_employee_linked_partner(self):
        user_partner = self.user_without_image.partner_id
        work_contact = self.employee_without_image.work_contact_id
        self.assertEqual(user_partner, work_contact)
        print('------TEST ADDITIONAL VOUCHER FIELDS OK--------------')