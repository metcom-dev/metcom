from odoo.tests.common import TransactionCase
from datetime import date, datetime
import pytz
from datetime import timedelta

class TestConvertDateToUTC(TransactionCase):

    def setUp(self):
        super(TestConvertDateToUTC, self).setUp()
        partner = self.env['res.partner'].create({
            'name': 'Employee address',
        })
        leave_23 = self.env.ref('holiday_process.hr_leave_type_23')
        self.employee = self.env['hr.employee'].create({
            'name': 'User Empl Employee',
            'address_home_id': partner.id,
            'leave_date_from': date.today(), 
            'leave_date_to': date.today() + timedelta(days=2)
        }) 
        self.ple_report = self.env['ple.report.inv.bal.one']
        self.leave_type = self.env['hr.leave.type'].create({
            'name': 'Test Leave Type',
            'code': 'TEST',
            'request_unit': 'hour',
        })
    def create_leave(self, employee, state, start_date, end_date):
        return self.env['hr.leave'].create({
            'name': 'Test Leave',
            'employee_id': self.employee.id,
            'holiday_status_id': self.leave_type.id,
            'date_from': datetime.combine(start_date, datetime.min.time()),
            'date_to': datetime.combine(end_date, datetime.min.time()),
            'state': state,
        })

    def _convert_date_timezone_to_utc(self, user, date_order_str, format_time='%Y-%m-%d %H:%M:%S'):
        tz = pytz.timezone(user.tz) if user.tz else pytz.utc
        date_order = datetime.strptime(date_order_str, format_time)
        datetime_with_tz = tz.localize(date_order, is_dst=None)
        date_order_utc = datetime_with_tz.astimezone(pytz.utc)
        return datetime.strftime(date_order_utc, format_time)

    def test_convert_date_timezone_to_utc(self):
        user = self.env['res.users'].create({
            'name': 'Test User',
            'login': 'testuser',
            'tz': 'Europe/Paris',
        })

        date_order_str = '2023-07-23 10:30:00'
        converted_date_order = self._convert_date_timezone_to_utc(user, date_order_str)
        expected_utc_date_order_str = '2023-07-23 08:30:00'
        self.assertEqual(converted_date_order, expected_utc_date_order_str)

        user.tz = 'America/New_York'
        date_order_str = '2023-07-23 10:30:00'

        converted_date_order = self._convert_date_timezone_to_utc(user, date_order_str)

        expected_utc_date_order_str = '2023-07-23 14:30:00'
        self.assertEqual(converted_date_order, expected_utc_date_order_str)
    
