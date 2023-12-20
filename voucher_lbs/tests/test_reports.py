from odoo.tests.common import TransactionCase
import datetime 
class TestReportVoucherLbs(TransactionCase):
    def setUp(self):
        super().setUp()
        self.hr_salary_rule_category = self.env['hr.salary.rule.category']
        self.hr_salary_rule_category_ing_001 = self.env.ref('basic_rule.hr_salary_rule_category_ing_001', False)
        self.hr_salary_rule_category_net = self.env.ref('hr_payroll.NET', False)
        self.payslip_model = self.env['hr.payslip']
        self.payslip_line_model = self.env['hr.payslip.line']
        self.leave_type_model = self.env['hr.leave.type']
        self.leave_model = self.env['hr.leave']
        partner = self.env['res.partner'].create({
            'name': 'Employee address',
        })
        self.employee = self.env['hr.employee'].create({
            'name': 'User Empl Employee',
            'address_home_id': partner.id,
        })  
    

    def test_get_report_values(self):
        payslip_obj = self.env['hr.payslip']
        payslip = payslip_obj.create({
            'name': 'Test Payslip',
            'employee_id': self.employee.id,  
        })
        print("FUNCIONA2----------------------------")
        report_obj = self.env['report.voucher_lbs.report_payslip_voucher_lbs']
        report_values = report_obj._get_report_values(docids=[payslip.id])

        self.assertIn('doc_ids', report_values)
        self.assertIn('docs', report_values)
        self.assertIn('data', report_values)
        self.assertIn('employer_sign', report_values)
        self.assertIn('lbs_lines', report_values)
        self.assertIn('lbs_total_values', report_values)
        print("FUNCIONA----------------------------")
  