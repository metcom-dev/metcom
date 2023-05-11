from odoo.tests import Form
from odoo.addons.hr_contract.tests.common import TestContractCommon
from datetime import date

class TestHrContract(TestContractCommon):

    def setUp(self):
        super().setUp()
        self.low_reason = self.env['low.reason'].create({
            'code': '2',
            'low_reason_description': 'low reason description example',
            'name': 'abv'
        })
        self.mintra_contract = self.env['mintra.contract'].create({
            'code': '1',
            'mintra_description': 'mintra  contract description example'
        })
        self.contract = self.env['hr.contract'].create({
            'name': 'Contract',
            'employee_id': self.employee.id,
            'state': 'open',
            'kanban_state': 'normal',
            'wage': 1,
            'date_start': date(2023, 1, 1),
            'date_end': date(2023, 1, 31),
            'reason_low_id': self.low_reason.id,
            'mintra_contract_id': self.mintra_contract.id,
            'compensation_in_kind': False
        })

    def test_employee_linked_contract(self):
        self.assertEqual(self.employee.contract_id, self.contract)
        print('------TEST ADDITIONAL PAYROLL FIELDS OK--------------')