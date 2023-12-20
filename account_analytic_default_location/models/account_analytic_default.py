from odoo import models, fields, api


class AccountAnalyticDefault(models.Model):
    _inherit = 'account.analytic.distribution.model'

    origin_warehouse_id = fields.Many2one(
        comodel_name='stock.warehouse',
        string='Almacén de Origen'
    )

    origin_location_id = fields.Many2one(comodel_name='stock.location', string='Ubicación de Origen')

    dest_location_id = fields.Many2one(comodel_name='stock.location', string='Ubicación de Destino')

    @api.model
    def account_get(self, product_id=None, partner_id=None, account_id=None, user_id=None, date=None, company_id=None, warehouse_id=None, location_id_01=None,
                    location_id_02=None):
        domain = []
        if product_id:
            domain += ['|', ('product_id', '=', product_id)]
        domain += [('product_id', '=', False)]
        if partner_id:
            domain += ['|', ('partner_id', '=', partner_id)]
        domain += [('partner_id', '=', False)]
        if account_id:
            domain += ['|', ('account_id', '=', account_id)]
        domain += [('account_id', '=', False)]
        if company_id:
            domain += ['|', ('company_id', '=', company_id)]
        domain += [('company_id', '=', False)]
        if user_id:
            domain += ['|', ('user_id', '=', user_id)]
        domain += [('user_id', '=', False)]
        if warehouse_id:
            domain += ['|', ('origin_warehouse_id', '=', warehouse_id)]
        domain += [('origin_warehouse_id', '=', False)]
        if location_id_01:
            domain += ['|', ('origin_location_id', '=', location_id_01)]
        domain += [('origin_location_id', '=', False)]
        if location_id_02:
            domain += ['|', ('dest_location_id', '=', location_id_02)]
        domain += [('dest_location_id', '=', False)]
        if date:
            domain += ['|', ('date_start', '<=', date), ('date_start', '=', False)]
            domain += ['|', ('date_stop', '>=', date), ('date_stop', '=', False)]
        best_index = -1
        res = self.env['account.analytic.distribution.model']
        for rec in self.search(domain):
            index = 0
            if rec.product_id:
                index += 1
            if rec.partner_id:
                index += 1
            if rec.account_id:
                index += 1
            if rec.company_id:
                index += 1
            if rec.user_id:
                index += 1
            if rec.date_start:
                index += 1
            if rec.date_stop:
                index += 1
            if index > best_index:
                res = rec
                best_index = index
        return res


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.depends('account_id', 'partner_id', 'product_id', 'move_id.stock_move_id')
    def _compute_analytic_distribution(self):
        for line in self:
            if line.display_type == 'product' or not line.move_id.is_invoice(include_receipts=True):
                distribution = self.env['account.analytic.distribution.model']._get_distribution({
                    'product_id': line.product_id.id,
                    'partner_id': line.partner_id.commercial_partner_id.id or line.move_id.partner_id.commercial_partner_id.id,
                    'product_categ_id': line.product_id.categ_id.id,
                    'partner_category_id': line.partner_id.category_id.ids,
                    'account_prefix': line.account_id.code,
                    'company_id': line.move_id.company_id.id,
                    'origin_warehouse_id': line.move_id.stock_move_id.picking_type_id.warehouse_id.id,
                    'origin_location_id': line.move_id.stock_move_id.location_id.id,
                    'dest_location_id': line.move_id.stock_move_id.location_dest_id.id
                })
                line.analytic_distribution = distribution or line.analytic_distribution
