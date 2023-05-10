from odoo.tests.common import TransactionCase


class TestHrPayslip(TransactionCase):

    def test__get_new_worked_days_lines(self):
        """Test that _get_new_worked_days_lines returns expected result."""

        # Create a payroll structure with two work entry types
        struct_days_ids = self.env['hr.work.entry.type'].create([
            {'name': 'Worked Day 1', 'code': 'WD1'},
            {'name': 'Worked Day 2', 'code': 'WD2'},
        ])
        payroll_structure = self.env['hr.payroll.structure'].create({
            'name': 'Payroll Structure',
            'struct_days_ids': [(6, 0, struct_days_ids.ids)],
        })

        # Create a payslip for an employee with worked days for both types
        employee = self.env['hr.employee'].create({'name': 'Employee'})
        payslip = self.env['hr.payslip'].create({
            'name': 'Payslip',
            'employee_id': employee.id,
            'struct_id': payroll_structure.id,
            'line_ids': [
                (0, 0, {'code': 'WD1', 'amount': 10}),
                (0, 0, {'code': 'WD2', 'amount': 20}),
            ],
        })
        print('-----------------------------------LINES OK ------------------------------------')
        # Call _get_new_worked_days_lines and assert the result
        result = payslip._get_new_worked_days_lines()
        expected = [
            (5, 0, 0),  # delete all existing worked days
            (0, 0, {'code': 'WD1', 'amount': 10}),  # add back the first worked day
            # exclude the second worked day because it's in the payroll structure
        ]
        self.assertEqual(result, expected)
        print('-----------------------------TESTING OK --------------------------------')