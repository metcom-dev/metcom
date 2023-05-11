from odoo.tests import Form
from odoo.addons.hr_contract.tests.common import TestContractCommon
from datetime import date

class TestHrContract(TestContractCommon):

    def setUp(self):
        super().setUp()
        payment_period = self.env['payment.period'].create({
            'code': 'codigo prueba',
            'payment_description': 'descripcion prueba',
            'name': 'nombre prueba'
        })
        payment_type = self.env['payment.type'].create({
            'code': 'codigo prueba',
            'payment_description': 'descripcion prueba',
            'name': 'nombre prueba'
        })
        special_situation = self.env['special.situation'].create({
            'code': 'codigo prueba',
            'situation_description': 'descripcion prueba',
            'name': 'nombre prueba'
        })

        variable_payment = self.env['variable.payment'].create({
            'code': 'codigo prueba',
            'name': 'nombre prueba'
        })
        specific_structure = self.env['hr.payroll.structure'].create({
            'name': 'End of the Year Bonus - Test',
            'schedule_pay_conditions': payment_period.id
        })
        structure_type = self.env['hr.payroll.structure.type'].create({
            'name': 'struct',
            'default_struct_id': specific_structure.id
        })
        self.contract = self.env['hr.contract'].create({
            'name': 'Contract',
            'employee_id': self.employee.id,
            'state': 'open',
            'kanban_state': 'normal',
            'wage': 1,
            'date_start': date(2023, 1, 1),
            'date_end': date(2023, 1, 31),
            'special_situation_id': special_situation.id,
            'payment_type_id': payment_type.id,
            'variable_payment_id': variable_payment.id,
            'structure_type_id': structure_type.id,

        })

    def test_employee_linked_contract(self):
        self.assertEqual(self.employee.contract_id, self.contract)
        self.assertEqual(self.employee.contract_id.structure_type_id.default_struct_id.schedule_pay_conditions, self.contract.schedule_pay_conditions)
        print('------TEST ADDITIONAL HR CONTRACT FIELDS OK--------------')

