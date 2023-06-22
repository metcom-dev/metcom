import unittest
from odoo.tests.common import TransactionCase


class TestSunatRegistro(TransactionCase):

    def setUp(self):
        super(TestSunatRegistro, self).setUp()

    def test_other_annexed_establishments(self):
        other_annexed = self.env['other.annexed.establishments'].create({
            'code': '001',
            'name': 'Annexed Establishment 1',
        })

        self.assertEqual(other_annexed.code, '001')
        self.assertEqual(other_annexed.name, 'Annexed Establishment 1')
        print('---------------------------- ANNEX OK ------------------------------')

    def test_industrial_classification(self):
        industrial_classification = self.env['international.industrial.classification'].create({
            'code': '001',
            'name': 'Industrial Classification 1',
        })

        self.assertEqual(industrial_classification.code, '001')
        self.assertEqual(industrial_classification.name, 'Industrial Classification 1')

    def test_account_move(self):
        partner = self.env['res.partner'].create({
            'name': 'Test Partner',
        })
        employee = self.env['hr.employee'].create({
            'name': 'Test Employee',
        })

        account_move = self.env['hr.contract'].create({
            'displacemnent': True,
            'employer_id': partner.id,
            'date_from_displacement': '2023-06-01',
            'date_to_displacement': '2023-06-30',
            'risk_activities': True,
            'given_service': 1,  # Assuming the ID of the industrial classification
            'worker_type_pensioner_provider': 1,  # Assuming the ID of the worker type
            'other_annexed': 1,  # Assuming the ID of the other annexed establishment
            'employee_id': employee.id,
        })
        print('------------------------PARTNER OK  ------------------------------')
        self.assertTrue(account_move.displacemnent)
        self.assertEqual(account_move.employer_id, partner)
        self.assertEqual(account_move.date_from_displacement, '2023-06-01')
        self.assertEqual(account_move.date_to_displacement, '2023-06-30')
        self.assertTrue(account_move.risk_activities)
        self.assertEqual(account_move.given_service, 1)
        self.assertEqual(account_move.worker_type_pensioner_provider, 1)
        self.assertEqual(account_move.other_annexed, 1)
        self.assertEqual(account_move.employee_id, employee)
        print('------------------------ TEST OK ------------------------------')

    def test_road_type_object(self):
        road_type = self.env['road.type.object'].create({
            'code': '001',
            'name': 'Road Type 1',
        })

        self.assertEqual(road_type.code, '001')
        self.assertEqual(road_type.name, 'Road Type 1')

    def test_zone_type_object(self):
        zone_type = self.env['zone.type.object'].create({
            'code': '001',
            'name': 'Zone Type 1',
        })

        self.assertEqual(zone_type.code, '001')
        self.assertEqual(zone_type.name, 'Zone Type 1')

    def test_ubigeo_reniec_object(self):
        ubigeo = self.env['ubigeo.reniec.object'].create({
            'code': '001',
            'name': 'Ubigeo 1',
        })

        self.assertEqual(ubigeo.code, '001')
        self.assertEqual(ubigeo.name, 'Ubigeo 1')

    def test_res_partner(self):
        road_type = self.env['road.type.object'].create({
            'code': '001',
            'name': 'Road Type 1',
        })
        zone_type = self.env['zone.type.object'].create({
            'code': '001',
            'name': 'Zone Type 1',
        })
        ubigeo = self.env['ubigeo.reniec.object'].create({
            'code': '001',
            'name': 'Ubigeo 1',
        })

        partner = self.env['res.partner'].create({
            'name': 'Test Partner',
            'road_type_id': road_type.id,
            'road_type_id_2': road_type.id,
            'road_type_id_3': road_type.id,
            'zone_type_id': zone_type.id,
            'ubigeo_code_id': ubigeo.id,
        })

        self.assertEqual(partner.name, 'Test Partner')
        self.assertEqual(partner.road_type_id, road_type)
        self.assertEqual(partner.road_type_id_2, road_type)
        self.assertEqual(partner.road_type_id_3, road_type)
        self.assertEqual(partner.zone_type_id, zone_type)
        self.assertEqual(partner.ubigeo_code_id, ubigeo)
        print('------------------------------- TEST OVER -------------------------------')
