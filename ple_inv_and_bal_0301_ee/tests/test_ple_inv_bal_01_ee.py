from odoo.tests import common
from odoo.tests.common import TransactionCase
from odoo.exceptions import AccessError
from odoo import _, fields, models, api, Command
from markupsafe import Markup
from odoo.tools import config

class TestAccountFinancialReportLine(TransactionCase):
    
    def setUp(self):
        super(TestAccountFinancialReportLine, self).setUp()        

    def test_eeff_ple_ids_field(self):       
        # Crear un registro en la tabla "account_report" con report_id igual a 22
        report = self.env['account.report'].create({
            'name': 'Test Report',
            'root_report_id': self.env.ref("account.generic_tax_report").id,
            'column_ids': [Command.create({'name': 'balance', 'sequence': 1, 'expression_label': 'balance'})],
            # Otros campos necesarios para "account.report"
        })

        # Crear un registro en la tabla "account.report.line" relacionado con el registro en "account_report"
        report_line = self.env['account.report.line'].create({
            'report_id': report.id,  # Usar el ID del registro en "account_report" creado anteriormente
            'name': 'Test Report Line',
            'eeff_ple_ids': 1,  
        })     
        self.assertEqual(report_line.eeff_ple_ids.id, 1)
        print("-----------------OK-------------------")  
        
class TestReportAccountFinancialReportInherit(common.TransactionCase):
    
    def setUp(self):
        super(TestReportAccountFinancialReportInherit, self).setUp()
        self.ReportModel = self.env['account.report']
        self.CompanyModel = self.env['res.company']
        self.WizardModel = self.env['wizard.report.generate.0301.ee']
        self.ViewRef = self.env.ref('ple_inv_and_bal_0301_ee.wizard_report_generate_0301_ee_txt_view')
        self.company = self.env['res.company'].create({'name': 'Test Company'})
        print("-----------------OK------------------")  

    def test_allow_txt_generation(self):
        report = self.ReportModel.create({
            'name': 'Test Report',
            'allow_txt_generation': '01'
        })
        self.assertEqual(report.allow_txt_generation, '01')
        print("-----------------OK3------------------")  
    def test_get_options(self):
        report = self.ReportModel.create({
            'name': 'Test Report',
            'allow_txt_generation': '01'
        })
        options = report._get_options()
        self.assertTrue('change_header' in options)
        self.assertEqual(options['change_header'], True)
        print("-----------------OK")  
    def test_init_options_buttons(self):
        report = self.ReportModel.create({
            'name': 'Test Report',
            'allow_txt_generation': '01',
            'company_id': self.company.id,
        })
        print("-----------------OK------------------")
    def test_open_report_export_txt_wizard_0301_ee(self):
        report = self.ReportModel.create({
            'name': 'Test Report',
            'allow_txt_generation': '01',
            'company_id': self.company.id,
        })
        options = {}
        wizard_action = report.open_report_export_txt_wizard_0301_ee(options)
        self.assertEqual(wizard_action['res_model'], 'wizard.report.generate.0301.ee')
        print("-----------------OK------------------")
    def test_get_pdf(self):
        report = self.ReportModel.create({
            'name': 'Test Report',
            'allow_txt_generation': '01',
            'company_id': self.company.id,          
        })      
        dummy_lines = self.env['account.report.line'].create([
            {'name': 'Line 1', 'report_id': report.id},
            {'name': 'Line 2', 'report_id': report.id},
        ])
        print("-----------------OK------------------")






