from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError

class base_test(TransactionCase):

    def setUp(self, *args, **kwargs):
        super(base_test, self).setUp(*args, **kwargs)
        self.lot_model = self.env['stock.lot']
        self.move_line_model = self.env['stock.move.line']

    def test_lot_status(self):
        lot = self.lot_model.create({
            'name': 'Lote de prueba',
        })

        self.assertFalse(lot.status)

        status = self.env['stock.lot.status'].create({
            'name': 'Status de prueba',
            'code': 'PRB'
        })
        lot.status = status

        self.assertEqual(lot.status, status)

    def test_move_line_status(self):
        lot = self.lot_model.create({
            'name': 'Lote de prueba',
        })
        move_line = self.move_line_model.create({
            'lot_id': lot.id,
        })

        self.assertFalse(move_line.status)

        status = self.env['stock.production.lot.status'].create({
            'name': 'Status de prueba',
        })
        move_line.status = status

        self.assertEqual(move_line.status, status)

    def test_inventory_line_status(self):
        lot = self.lot_model.create({
            'name': 'Lote de prueba',
        })
        inventory_line = self.env['stock.quant'].create({
            'lot_id': lot.id,
        })

        expected_status = "%s - %s" % (lot.status.code, lot.status.name)
        self.assertEqual(inventory_line.status, expected_status)

    def test_update_status(self):
        lot = self.lot_model.create({
            'name': 'Lote de prueba',
        })
        move_line = self.move_line_model.create({
            'lot_id': lot.id,
        })

        status = self.env['stock.production.lot.status'].create({
            'name': 'Status de prueba',
        })
        move_line.status = status

        picking = self.env['stock.picking'].create({})
        picking.move_line_ids_without_package = move_line
        picking.button_validate()

        self.assertEqual(lot.status, status)

    def test_update_status_validation_error(self):
        picking = self.env['stock.picking'].create({})
        with self.assertRaises(ValidationError):
            picking.button_validate()
