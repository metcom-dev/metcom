from odoo.tests.common import TransactionCase

# docker exec -it 160-odoo-1 /bin/bash
#cd opt/odoo_dir/odoo/
#./odoo-bin -c /etc/odoo/odoo.conf -i account_analytic_default_location --test-enable -p 8065 -d Mig_taller_sept --stop-after-init

class TestAccountAnalyticDefault(TransactionCase):

    def setUp(self):
        super().setUp()
        self.warehouse01 = self.env['stock.warehouse'].search([('company_id', '=', self.env.company.id)], limit=1)
        self.wh01_address = self.env['res.partner'].create({
            'name': 'Address 1',
            'parent_id': self.env.company.id,
            'type': 'delivery',
        })


    def test_warehouse_partner_id(self):
        self.warehouse01.partner_id = self.wh01_address
        self.assertEqual(self.warehouse01.partner_id, self.wh01_address)
        print('--TEST OK - test_warehouse_partner_id--')

    def test_origin_warehouse(self):
        account_analytic_default = self.env['account.analytic.distribution.model'].create({
            'origin_warehouse_id': self.warehouse01.id,
            'origin_location_id': self.warehouse01.lot_stock_id.id,
        })
        self.assertEqual(account_analytic_default.origin_warehouse_id, self.warehouse01)
        self.assertEqual(account_analytic_default.origin_location_id, self.warehouse01.lot_stock_id)
        print('--TEST OK - test_origin_warehouse--')
