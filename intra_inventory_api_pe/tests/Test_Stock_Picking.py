from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError

class Test_Stock_Picking(TransactionCase):

    def setUp(self, *args, **kwargs):
        super(Test_Stock_Picking, self).setUp(*args, **kwargs)
        self.picking_model = self.env['stock.picking']
        self.config_settings_model = self.env['res.config.settings']

    def test_sync_status_picking(self):
        picking = self.picking_model.create({
            'name': 'Picking de prueba',
            'sync_status_picking': 'blocked',
            'state': 'done',
        })

        self.assertEqual(picking.sync_status_picking, 'blocked')
        picking.action_sync_tinka_stock_picking()
        self.assertEqual(picking.sync_status_picking, 'done')

    def test_no_report_stock_picking(self):
        picking = self.picking_model.create({
            'name': 'Picking de prueba',
            'sync_status_picking': 'blocked',
        })

        picking.no_report_stock_picking()
        self.assertEqual(picking.sync_status_picking, 'normal')

    def test_button_validate(self):
        picking = self.picking_model.create({
            'name': 'Picking de prueba',
            'sync_status_picking': 'blocked',
            'state': 'done',
        })

        picking.button_validate()
        self.assertEqual(picking.sync_status_picking, 'done')

    def test_find_between(self):
        string = "[Texto entre corchetes]"
        result = self.picking_model.find_between(string, "[", "]")
        self.assertEqual(result, "Texto entre corchetes")

    def test_api_intralot(self):
        config_settings = self.config_settings_model.create({
            'name': 'Configuración de prueba',
        })

        token = config_settings.action_api_intralot()
        self.assertTrue(token)
