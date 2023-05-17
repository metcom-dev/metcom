from odoo import models, fields, api, _
from odoo.exceptions import UserError



class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'
    _description = 'Register Payment'

    @api.depends('source_amount', 'source_amount_currency', 'source_currency_id', 'company_id', 'currency_id', 'payment_date')
    def _compute_amount(self):
        for wizard in self:
            wizard.amount = wizard.source_amount_currency

    @api.depends('journal_id')
    def _compute_currency_id(self):
        for wizard in self:
            wizard.currency_id = wizard.source_currency_id or wizard.journal_id.currency_id or wizard.company_id.currency_id
