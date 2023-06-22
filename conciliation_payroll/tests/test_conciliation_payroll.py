from datetime import datetime
from odoo.addons.hr_payroll.tests.common import TestPayslipContractBase
from odoo.tests import tagged

@tagged('2_weeks_calendar')
class TestPayslipContractCalendar2Weeks(TestPayslipContractBase):

    def test_contract_2_weeks(self):
        # Create a payslip for a month with a contract with 2 weeks period.
        payslip = self.env['hr.payslip'].create({
            'name': 'November 2015',
            'employee_id': self.jules_emp.id,
            'date_from': datetime.strptime('2015-11-01', '%Y-%m-%d'),
            'date_to': datetime.strptime('2015-11-30', '%Y-%m-%d'),
        })

    def test_01_compute_has_reconciled_entries(self):
        employees = self.env['hr.payslip.employees'].create({'employee_ids': [(6, 0, [self.jules_emp.id])]})
        self.payslip_1 = self._create_payslip(self.jules_emp, date_from='2023-01-01', date_to='2023-01-15')
        self.payslip_2 = self._create_payslip(self.jules_emp, date_from='2023-01-16', date_to='2023-01-31')
        self.payment.payslip_ids = [(6, 0, [self.payslip_1.id, self.payslip_2.id])]
        self.payment.action_generate_move()
        self.assertTrue(self.payment.move_id, 'Payment move should be created')


    # ./odoo-bin -c /etc/odoo/odoo.conf -i conciliation_payroll --test-enable -p 8065 -d MIG_TEST_16 --stop-after-init
