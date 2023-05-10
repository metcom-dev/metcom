from odoo import models, fields, api, _


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    def _create_payment_vals_from_batch(self, batch_result):
        values = super()._create_payment_vals_from_batch(batch_result)
        values = {'to_force_exchange_rate': self._context.get('to_force_exchange_rate'), **values}
        return values

    def _create_payment_vals_from_wizard(self, batch_result):
        payment_vals = super()._create_payment_vals_from_wizard(batch_result)
        payment_vals['to_force_exchange_rate'] = self._context.get('to_force_exchange_rate')
        return payment_vals
