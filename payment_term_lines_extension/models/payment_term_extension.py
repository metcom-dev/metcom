from odoo import api, fields, models, Command, _
from odoo.exceptions import UserError, ValidationError


class PaymentTermLineExtension(models.Model):
    _name = "account.payment.term.line.extension"
    _description = 'Account Payment Term Line Extension'

    payment_term_line_id = fields.Many2one('account.payment.term.line')
    currency = fields.Many2one(
        comodel_name='res.currency',
        string='Moneda',
        required=False
    )
    ledger_account = fields.Many2one(
        comodel_name='account.account',
        string='Cuenta contable por cobrar',
        default=False,
        help="Al colocar una cuenta contable, el plazo de pago se generará en esa cuenta contable.",
        required=False,
        company_dependent=True
    )
    ledger_account_payable = fields.Many2one(
        comodel_name='account.account',
        string='Cuenta contable por pagar',
        default=False,
        required=False,
        company_dependent=True
    )


class AccountPaymentTermLine(models.Model):
    _inherit = "account.payment.term.line"

    def _default_term_line_ids(self):
        return [Command.create({'currency': 'balance', 'ledger_account': '', 'ledger_account_payable': ''})]

    factor_round = fields.Float(
        string="Factor de Redondeo",
        digits="Account",
        help="En este campo se colocará el factor por el cual quiere que se redondee la línea del término de plazo, "
             "si quiere que salga sin decimales, colocar 1.00.",
    )
    day_of_the_month = fields.Integer(string='Day of the month',
                                      help="Day of the month on which the invoice must come to its term. If zero or negative, this value will be ignored, and no specific day will be set. If greater than the last day of a month, this number will instead select the last day of this month.")
    option = fields.Selection([
        ('day_after_invoice_date', 'Day(s) after the invoice date'),
        ('after_invoice_month', 'After the invoice month'),
        ('day_following_month', 'Day(s) of the following month'),
        ('day_current_month', 'Day(s) of the current month')
    ], string='Option', default='day_after_invoice_date')
    currency = fields.Many2one(
        'res.currency',
        string='Moneda',
        required=False
    )
    ledger_account = fields.Many2one(
        'account.account',
        string='Cuenta contable por cobrar',
        default=False,
        help="Al colocar una cuenta contable, el plazo de pago se generará en esa cuenta contable.",
        required=False,
        company_dependent=True
    )
    ledger_account_payable = fields.Many2one(
        'account.account',
        string='Cuenta contable por pagar',
        default=False,
        required=False,
        company_dependent=True
    )
    term_extension = fields.One2many(
        'account.payment.term.line.extension',
        string='Cuenta contables',
        inverse_name='payment_term_line_id',
        default=_default_term_line_ids,
    )

    def _get_data_from_line_ids(self, date_ref):
        res = super(AccountPaymentTermLine, self)._get_data_from_line_ids(date_ref)
        res['term_extension'] = self.term_extension
        return res

    @api.onchange('option')
    def _onchange_option(self):
        if self.option in ('day_current_month', 'day_following_month'):
            self.days = 0

    @api.constrains('days')
    def _check_days(self):
        for term_line in self:
            if term_line.option in ('day_following_month', 'day_current_month') and term_line.days <= 0:
                raise ValidationError(_("The day of the month used for this term must be strictly positive."))
            elif term_line.days < 0:
                raise ValidationError(_("The number of days used for a payment term cannot be negative."))