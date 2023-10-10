from odoo.tests.common import TransactionCase
from odoo.tools import mute_logger

class TestWizardReportGenerateTxt(TransactionCase):

    def setUp(self):
        super().setUp()
        self.wizard_data = {
            'report_model': 'account.report', 
            'report_id': 948, 
            'company_id': self.env.ref('base.main_company').id,  
            'date_start': '2023-01-01',
            'date_end': '2023-12-31',
            'state_send': '0',
            'date_ple': '2023-08-11',
            'financial_statements_catalog': '01',
            'eeff_presentation_opportunity': '01',
        }
        print("-----------------OK-------------------")  
    @mute_logger('odoo.addons.base.models.ir_actions_report')
    def test_generate_data(self):
        report_data = {
            'name': 'Test Report',
            'id': 2,
        }
        self.env['account.report'].create(report_data)
        eeff_data = {
            'name': 'ESF Test',
            'eeff_type': '3.1',
            'code': 123,
            'description': 'ESF DEMO2' 
        }
        eeff = self.env['eeff.ple'].create(eeff_data)
        self.wizard_data['report_id'] = eeff.id
        wizard = self.env['wizard.report.generate.0301.ee'].create(self.wizard_data)       
        line_data = {
            'report_id': 1,
            'eeff_ple_ids': eeff.id,
            'name': 'Line 1'           
        }    
        line = self.env['account.report.line'].create(line_data)
        print("-----------------OK-------------------")       
    def test__generate_periods_options_list(self):
        wizard = self.env['wizard.report.generate.0301.ee'].create(self.wizard_data)
        date_options = {'mode': 'range', 'date_from': '2023-01-01', 'date_to': '2023-12-31'}
        periods_options_list = wizard._generate_periods_options_list(date_options)
        self.assertTrue(periods_options_list)
        self.assertEqual(periods_options_list[0]['mode'], 'range')
        print("-----------------OK-------------------")  
    def test_action_return_wizard(self):
        wizard = self.env['wizard.report.generate.0301.ee'].create(self.wizard_data)
        action = wizard.action_return_wizard()
        self.assertTrue(action)
        self.assertEqual(action['res_model'], 'wizard.report.generate.0301.ee')
        print("-----------------OK-------------------")  
