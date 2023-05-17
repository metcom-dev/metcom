from odoo.tests import Form
from odoo.addons.hr_contract.tests.common import TestContractCommon
from datetime import date

class TestHrContract(TestContractCommon):

    def setUp(self):
        super().setUp()
        mail_values = {
            'name': 'TestTemplate',
            'subject': 'About {{ object.name }}',
            'body_html': '<p>Hello <t t-out="object.name"/></p>',
        }
        email_template = self.env['mail.template'].create(mail_values)

        self.contract = self.env['hr.contract'].create({
            'name': 'Contract',
            'employee_id': self.employee.id,
            'state': 'open',
            'kanban_state': 'normal',
            'wage': 1,
            'date_start': date(2023, 1, 1),
            'date_end': date(2023, 1, 31),
            'service_duration': 'prueba service duration',
            'additional_info': 'informacion adifional prueba',
            'contract_name': 'nombre contrato prueba',
            'contract_template_id': email_template.id
        })

    def test_employee_linked_contract(self):
        self.assertEqual(self.employee.contract_id, self.contract)
        print('------TEST Payment_conditions FIELDS OK--------------')

