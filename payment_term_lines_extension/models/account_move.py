from odoo import api, fields, models, _


class AccountMove(models.Model):
    _inherit = "account.move"

    # @api.onchange('invoice_payment_term_id', 'currency_id')
    # def _onchange_account_id(self):
    #     self.ensure_one()
    #     currency = self.currency_id
    #     account_id = None
    #     # for payment_term in self.invoice_payment_term_id.line_ids:
    #     #     if payment_term.l10n_pe_is_detraction_retention:
    #     #         for term_extension in payment_term.term_extension:
    #     #             if term_extension.currency == currency:
    #     #                 account_id = term_extension.ledger_account
    #
    #     for line in self.line_ids:
    #         if line.display_type == "payment_term":
    #             if account_id:
    #                 line.account_id = account_id

    # Ejecuta funcionalidad del módulo automatic_account_change, para que pueda funcionar junto a este
    # self._get_change_account()

    def _get_payment_terms_account(self):
        ''' Get the account from invoice that will be set as receivable / payable account.
        :param self:                    The current account.move record.
        :param payment_terms_lines:     The current payment terms lines.
        :return:                        An account.account record.
        '''
        if self.partner_id:
            # Retrieve account from partner.
            if self.is_sale_document(include_receipts=True):
                return self.partner_id.property_account_receivable_id
            else:
                return self.partner_id.property_account_payable_id
        else:
            # Search new account.
            domain = [
                ('company_id', '=', self.company_id.id),
                ('internal_type', '=', 'receivable' if self.move_type in ('out_invoice', 'out_refund', 'out_receipt') else 'payable'),
                ('deprecated', '=', False),
            ]
            return self.env['account.account'].search(domain, limit=1)

    def _get_data_from_account_payment_term_lines(self, term):
        res = super(AccountMove, self)._get_data_from_account_payment_term_lines(term)
        new_account = self._get_payment_terms_account()
        account_line_ids = term['term_extension']

        account_line = account_line_ids.search([('currency.id', '=', self.currency_id.id), ('id', 'in', account_line_ids.ids)], limit=1)
        ledger_account_related = account_line.ledger_account
        ledger_account_payable_related = account_line.ledger_account_payable

        if ledger_account_related and self.move_type in ('out_invoice', 'out_refund', 'out_receipt'):
            new_account = ledger_account_related
        elif ledger_account_payable_related and self.move_type in ('in_invoice', 'in_refund', 'in_receipt'):
            new_account = ledger_account_payable_related
        res['term_account_id'] = new_account.id if new_account else False
        return res

    def _set_payment_terms_account(self, payment_terms_lines):
        for line in payment_terms_lines:
            if line.term_account_id:
                line.account_id = line.term_account_id

    @api.depends('display_type', 'company_id')
    def _compute_account_id(self):
        term_lines = self.filtered(lambda x: x.display_type == 'payment_term')
        if term_lines:
            self._set_payment_terms_account(term_lines)

        product_lines = self.filtered(lambda x: x.display_type == 'product' and x.move_id.is_invoice(True))
        for line in product_lines:
            if line.product_id:
                fiscal_position = line.move_id.fiscal_position_id
                accounts = line.with_company(line.company_id).product_id \
                    .product_tmpl_id.get_product_accounts(fiscal_pos=fiscal_position)
                if line.move_id.is_sale_document(include_receipts=True):
                    line.account_id = accounts['income'] or line.account_id
                elif line.move_id.is_purchase_document(include_receipts=True):
                    line.account_id = accounts['expense'] or line.account_id
            elif line.partner_id:
                line.account_id = self.env['account.account']._get_most_frequent_account_for_partner(
                    company_id=line.company_id.id,
                    partner_id=line.partner_id.id,
                    move_type=line.move_id.move_type,
                )
        for line in self:
            if not line.account_id and line.display_type not in ('line_section', 'line_note'):
                previous_two_accounts = line.move_id.line_ids.filtered(
                    lambda l: l.account_id and l.display_type == line.display_type
                )[-2:].account_id
                if len(previous_two_accounts) == 1 and len(line.move_id.line_ids) > 2:
                    line.account_id = previous_two_accounts
                else:
                    line.account_id = line.move_id.journal_id.default_account_id


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    term_account_id = fields.Many2one(comodel_name='account.account', string='Parametro temporal para tener calculado cuenta de la linea del término de pago')
