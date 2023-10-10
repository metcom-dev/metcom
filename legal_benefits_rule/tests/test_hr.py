from datetime import datetime
from odoo.tests.common import TransactionCase


class TestHr(TransactionCase):

    def setUp(self, *args, **kwargs):
        super(TestHr, self).setUp(*args, **kwargs)
        self.employee = self.env['hr.employee'].create({'name': 'Test Employee'})
        self.calendar = self.env['resource.calendar'].create({
            'name': 'Test Calendar',
            'hours_per_day': 8.0,  # Ajusta las horas por día según tus necesidades
            # Añade más campos según los requerimientos del calendario
        })
        self.contract = self.env['hr.contract'].create({
            'name': 'Test Contract',
            'employee_id': self.employee.id,
            'resource_calendar_id': self.calendar.id,
            'date_start': datetime.now().strftime('%Y-%m-%d'),
            'wage': 0.0,  # Agrega este campo y establece un valor adecuado
        })
        self.payslip = self.env['hr.payslip'].create({
            'name': 'Test Payslip',
            'employee_id': self.employee.id,
            'date_from': datetime.now().strftime('%Y-01-01'),
            'date_to': datetime.now().strftime('%Y-01-31'),
            'contract_id': self.contract.id,
        })

        def test_get_worked_day_lines(self):
            # Agrega las líneas de trabajo (worked_days) necesarias al objeto payslip
            tdi_001_entry_type_id = self.env.ref('legal_benefits_rule.hr_work_entry_type_tdi_001')
            tdi_002_entry_type_id = self.env.ref('legal_benefits_rule.hr_work_entry_type_tdi_002')

            self.payslip.write({
                'worked_days_line_ids': [
                    (0, 0, {'code': 'TDI_001', 'number_of_days': 5, 'work_entry_type_id': tdi_001_entry_type_id.id}),
                    (0, 0, {'code': 'TDI_002', 'number_of_days': 10, 'work_entry_type_id': tdi_002_entry_type_id.id}),
                ]
            })

            # Llama al método _get_worked_day_lines para realizar el cálculo
            self.payslip._get_worked_day_lines()

            # Verifica los resultados esperados
            tdi_001_days = self.payslip.worked_days_line_ids.filtered(lambda line: line.code == 'TDI_001').number_of_days
            tdi_002_days = self.payslip.worked_days_line_ids.filtered(lambda line: line.code == 'TDI_002').number_of_days

            self.assertEqual(tdi_001_days, 5, 'testito1')
            self.assertEqual(tdi_002_days, 10, 'testito2')


