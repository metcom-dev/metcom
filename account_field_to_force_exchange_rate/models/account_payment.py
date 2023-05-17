from odoo import fields, models


class AccountPayment(models.Model):
    _inherit = "account.payment"

    to_force_exchange_rate = fields.Float(
        string='Forzar T.C.',
        digits=(12, 12),
        help='This labels is used for force exchange rate.'
    )
