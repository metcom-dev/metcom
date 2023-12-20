from odoo.tests.common import TransactionCase
from odoo import fields


class TestFilterUtilities(TransactionCase):

    def test_hr_leave_utilities(self):
        hr_leave = self.env['hr.leave'].create({'name': 'Leave 1'})
        self.assertFalse(hr_leave.utilities, "Utilities should be False by default")

        holiday_status = self.env['hr.leave.type'].create({
            'name': 'Leave Type',
            'utilities': True
        })
        hr_leave.holiday_status_id = holiday_status
        self.assertTrue(hr_leave.utilities, "Utilities should be True after related field assignment")
        print('------------------TEST LEAVE ---------------------')


    def test_hr_attendance_utilities(self):
        hr_attendance = self.env['hr.attendance'].create({'name': 'Attendance 1'})
        self.assertFalse(hr_attendance.utilities, "Utilities should be False by default")

        holiday_status = self.env['hr.leave.type'].create({
            'name': 'Leave Type',
            'utilities': True
        })
        hr_attendance.holiday_status_id = holiday_status
        self.assertTrue(hr_attendance.utilities, "Utilities should be True after related field assignment")

    def test_hr_payslip_worked_days_utilities(self):
        hr_payslip_worked_days = self.env['hr.payslip.worked_days'].create({'name': 'Worked Days 1'})
        self.assertFalse(hr_payslip_worked_days.utilities, "Utilities should be False by default")

        work_entry_type = self.env['hr.work.entry.type'].create({
            'name': 'Work Entry Type',
            'utilities': True
        })
        hr_payslip_worked_days.work_entry_type_id = work_entry_type
        self.assertTrue(hr_payslip_worked_days.utilities, "Utilities should be True after related field assignment")
        print('-----------------------------  TEST OK  ----------------------------------')
