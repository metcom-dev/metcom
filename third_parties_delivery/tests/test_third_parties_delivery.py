from odoo.tests import common


class TestThirdPartiesDelivery(common.TransactionCase):

    def test_create_delivery(self):
        partner = self.env['res.partner'].create({
            'name': 'Test Customer',
            'email': 'test_customer@example.com'
        })

        picking = self.env['stock.picking'].create({
            'partner_id': partner.id,
            'picking_type_id': 1,
            'location_id': 2,
            'location_dest_id': 3
        })

        self.assertEqual(picking.customer_id, partner)

        print('-------------------------THIRD PARTY DELIVERY TEST OK--------------------------')
