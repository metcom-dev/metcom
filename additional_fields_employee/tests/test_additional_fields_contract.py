from odoo.tests import Form
from odoo.addons.hr_contract.tests.common import TestContractCommon
from datetime import date

class TestHrContract(TestContractCommon):

    def setUp(self):
        super().setUp()
        self.employee_regime = self.env['employee.regime'].create({
            'code': '2345',
            'regime_description': 'regime description example',
            'name': 'example name',
            'private_sector': False,                    'public_sector': True,
            'other_entities': False,
            'is_mype': False
        })
        self.type_contract = self.env['type.contract'].create({
            'code': '2',
            'contract_type': 'contract type description example',
            'name': 'abv'
        })
        self.work_occupation = self.env['work.occupation'].create({
            'code': '1',
            'name': 'worker',
            'executive': False,
            'employee': True,
            'worker': True
        })
        self.contract = self.env['hr.contract'].create({
            'name': 'Contract',
            'employee_id': self.employee.id,
            'state': 'open',
            'kanban_state': 'normal',
            'wage': 1,
            'date_start': date(2023, 1, 1),
            'date_end': date(2023, 1, 31),
            'labor_regime_id': self.employee_regime.id,
            'labor_condition_id': self.type_contract.id,
            'work_occupation_id': self.work_occupation.id,
            'maximum_working_day': True,
            'atypical_cumulative_day': False,
            'nocturnal_schedule': True,
            'unionized': False,
            'is_practitioner': False
        })

    def test_employee_linked_contract(self):
        self.assertEqual(self.employee.contract_id, self.contract)
        print('------TEST ADDITIONAL HR CONTRACT FIELDS OK--------------')

