from odoo.tests import common
from odoo.tests.common import TransactionCase
from odoo.exceptions import AccessError
from odoo import _, fields, models, api
from markupsafe import Markup
from odoo.tools import config

class TestAccountFinancialReportLine(TransactionCase):
    
    def setUp(self):
        super(TestAccountFinancialReportLine, self).setUp()        

    def test_re_item_field(self):       
        report_line = self.env['account.report.line'].create({
            'report_id': 22,
            'name': 'Test Report Line',
            're_item': 1,  
        })     
        self.assertEqual(report_line.re_item.id, 1)
        print("-----------------OK-------------------")  
        
class TestReportAccountFinancialReportInherit(common.TransactionCase):
    
    def setUp(self):
        super(TestReportAccountFinancialReportInherit, self).setUp()
        self.ReportModel = self.env['account.report']
        self.CompanyModel = self.env['res.company']
        self.WizardModel = self.env['wizard.report.generate.txt']
        self.ViewRef = self.env.ref('ple_inv_and_bal_0320_ee.wizard_report_generate_txt_view')
        self.company = self.env['res.company'].create({'name': 'Test Company'})
        print("-----------------OK------------------")  

    def test_allow_txt_generation(self):
        report = self.ReportModel.create({
            'name': 'Test Report',
            'allow_txt_generation': '20'
        })
        self.assertEqual(report.allow_txt_generation, '20')
        print("-----------------OK3------------------")  
    def test_get_options(self):
        report = self.ReportModel.create({
            'name': 'Test Report',
            'allow_txt_generation': '20'
        })
        options = report._get_options()
        self.assertTrue('change_header' in options)
        self.assertEqual(options['change_header'], True)
        print("-----------------OK")  
    def test_init_options_buttons(self):
        report = self.ReportModel.create({
            'name': 'Test Report',
            'allow_txt_generation': '20',
            'company_id': self.company.id,
        })
        print("-----------------OK------------------")
    def test_open_report_export_txt_wizard(self):
        report = self.ReportModel.create({
            'name': 'Test Report',
            'allow_txt_generation': '20',
            'company_id': self.company.id,
        })
        options = {}
        wizard_action = report.open_report_export_txt_wizard(options)
        self.assertEqual(wizard_action['res_model'], 'wizard.report.generate.txt')
        print("-----------------OK------------------")
    def test_get_pdf(self):
        report = self.ReportModel.create({
            'name': 'Test Report',
            'allow_txt_generation': '20',
            'company_id': self.company.id,          
        })      
        dummy_lines = self.env['account.report.line'].create([
            {'name': 'Line 1', 'report_id': report.id},
            {'name': 'Line 2', 'report_id': report.id},
        ])
        print("-----------------OK------------------")






