from odoo import fields, models


class AccountAsset(models.Model):
    _inherit = 'account.asset'

    READONLY_STATES = {
        'model': [('readonly', True)],
        'open': [('readonly', True)],
        'paused': [('readonly', True)],
        'close': [('readonly', True)],
        'cancelled': [('readonly', True)]
    }

    currency_id = fields.Many2one(
        comodel_name='res.currency',
        string='Moneda',
        required=True,
        related=False,
        store=True,
        state=READONLY_STATES,
        default=lambda self: self.env.company.currency_id.id
    )

    def compute_depreciation_board(self):
        self.ensure_one()
        new_depreciation_moves_data = self._recompute_board()

        # Need to unlink draft move before adding new one because if we create new move before, it will cause an error
        # in the compute for the depreciable/cumulative value
        self.depreciation_move_ids.filtered(lambda mv: mv.state == 'draft').unlink()
        new_depreciation_moves = self.env['account.move'].create(new_depreciation_moves_data)
        for new_depreciation_move in new_depreciation_moves:
            new_depreciation_move.with_context(check_move_validity=False)._onchange_currency_move_type_entry()

        if self.state == 'open':
            # In case of the asset is in running mode, we post in the past and set to auto post move in the future
            new_depreciation_moves._post()

        return True

    def _recompute_board(self):
        depreciation_moves = super()._recompute_board()

        if self.currency_id != self.company_id.currency_id:
            to_force_exchange_rate = self._get_to_force_exchange_rate()
            for move in depreciation_moves:
                move['to_force_exchange_rate'] = to_force_exchange_rate

        return depreciation_moves

    def _get_to_force_exchange_rate(self):
        return self.env['res.currency']._get_conversion_rate(
            from_currency=self.company_id.currency_id,
            to_currency=self.currency_id,
            company=self.company_id,
            date=self.acquisition_date or fields.Date.context_today(self),
        )
