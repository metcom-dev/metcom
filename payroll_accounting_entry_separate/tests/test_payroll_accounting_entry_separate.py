from odoo.tests import tagged
from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError
from datetime import date

@tagged('-at_install', 'post_install')
class TestHrPayslip(TransactionCase):

    def setUp(self):
        super().setUp()
        self.company_temp = self.env['res.company'].create({
            'name': 'Company test',
        })

        self.account_dc = self.env['account.account'].create({
            'name': 'Test Debit Account',
            'code': 'TDA',
            'company_id': self.company_temp.id,
            'account_type': 'asset_receivable',
            'create_asset': 'no',
        })
        self.journal_temp = self.env['account.journal'].create({
            'name': 'Test Journal',
            'type': 'general',
            'code': 'TJ',
            'company_id': self.company_temp.id,
            'invoice_reference_model': 'odoo',
            'invoice_reference_type': 'none',
            'default_account_id': self.account_dc.id,
        })
        self.calendar_temp = self.env['resource.calendar'].create({
            'name': 'Test Calendar',
            # 'tz': ' ',
        })
        self.resource_temp = self.env['resource.resource'].create({
            'name': 'Test Resource',
            'resource_type': 'user',
            'time_efficiency': 40.0,
            # 'tz': ' ',
            'calendar_id': self.calendar_temp.id,
        })
        self.employee_temp = self.env['hr.employee'].create({
            'company_id': self.company_temp.id,
            'employee_type': 'employee',
            'resource_id': self.resource_temp.id,
        })
        self.hr_payslip = self.env['hr.payslip'].create({
            'company_id': self.company_temp.id,
            'date_from': date(2023,7, 1),
            'date_to': date(2023,7, 31),
            'name': 'Test Payslip',
            'employee_id': self.employee_temp.id,
            'journal_id': self.journal_temp.id,
            'number': '0001',
        })

    def test_1_prepare_adjust_line(self):
        line_ids = []
        adjust_type = 'credit'
        debit_sum = 1000.0
        credit_sum = 1500.0
        date = '2023-07-21',

        with self.assertRaises(UserError):
            self.hr_payslip._prepare_adjust_line(line_ids, adjust_type, debit_sum, credit_sum, date)
        print("--------------------------------------------------TEST 1----------------------------------------------------")

    def test_2_action_create_account_move(self):
        self.hr_payslip._action_create_account_move()
        self.assertTrue(self.hr_payslip._action_create_account_move())
        self.assertTrue(self.hr_payslip.move_id.fields_get(), "No se creó move_id en el objeto payslip")
        print("--------------------------------------------------TEST 2----------------------------------------------------")
