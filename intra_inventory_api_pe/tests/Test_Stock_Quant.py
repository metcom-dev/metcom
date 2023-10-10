from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError

class Test_Stock_Quant(TransactionCase):

    def setUp(self, *args, **kwargs):
        super(Test_Stock_Quant, self).setUp(*args, **kwargs)
        self.quant_model = self.env['stock.quant']
        self.config_settings_model = self.env['res.config.settings']

    def test_sync_status_inventory(self):
        quant = self.quant_model.create({
            'name': 'Quant de prueba',
            'sync_status_inventory': 'blocked',
        })

        self.assertEqual(quant.sync_status_inventory, 'blocked')
        quant.action_sync_tinka_stock_inventory()
        self.assertEqual(quant.sync_status_inventory, 'done')

    def test_no_report_stock_inventory(self):
        quant = self.quant_model.create({
            'name': 'Quant de prueba',
            'sync_status_inventory': 'blocked',
        })

        quant.no_report_stock_inventory()
        self.assertEqual(quant.sync_status_inventory, 'normal')

    def test_action_apply_inventory(self):
        quant = self.quant_model.create({
            'name': 'Quant de prueba',
            'sync_status_inventory': 'blocked',
        })

        quant.action_apply_inventory()
        self.assertEqual(quant.sync_status_inventory, 'done')

    def test_api_intralot(self):
        config_settings = self.config_settings_model.create({
            'name': 'Configuración de prueba',
        })

        token = config_settings.action_api_intralot()
        self.assertTrue(token)
