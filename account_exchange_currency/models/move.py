from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    exchange_rate = fields.Float(
        string='Tipo de Cambio',
        digits=(12, 6),
        compute='_compute_currency_rate',
        store=True
    )

    @api.depends('currency_id', 'company_id', 'exchange_rate')
    def _compute_currency_rate(self):
        super()._compute_currency_rate()

    @api.depends('currency_id', 'invoice_date', 'date')
    def _compute_currency_rate(self):
        for obj in self:
            obj.exchange_rate = obj._get_actual_currency_rate()

    def _get_actual_currency_rate(self):
        if self.currency_id:
            if self.date and self.date != self.invoice_date:
                date = self.date
            else:
                date = self.invoice_date or fields.Date.today()
            company = self.company_id
            currency_rates = self.currency_id._get_rates(company, date)
            exchange_rate = currency_rates.get(self.currency_id.id) or 1.0
            rate = 1 / (exchange_rate or 1)
        else:
            rate = 1
        return rate


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.depends('currency_id', 'company_id', 'move_id.date', 'move_id.exchange_rate')
    def _compute_currency_rate(self):
        super()._compute_currency_rate()
        for line in self:
            line.set_currency_date_by_exchange_rate()

    def set_currency_date_by_exchange_rate(self):
        if self.currency_id and self.currency_id != self.company_currency_id and self.move_id.exchange_rate != 0.0:
            self.currency_rate = 1 / self.move_id.exchange_rate
