from odoo import api, models, fields

import logging
log = logging.getLogger(__name__)

class ReportPurchaseOrder(models.AbstractModel):
    _name = 'report.purchase.report_purchaseorder'
    _description = "Valores para reporte de Orden de Compra"

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['purchase.order'].browse(docids)
        order_lines = docs.order_line
        analytic_distribution_names = []
        bank_name = ''
        account_number = ''
        bank_bic = ''

        currency_id = docs.currency_id
        bank_type = docs.bank_type
        if docs.partner_id.bank_ids:
            for bank in docs.partner_id.bank_ids:
                if bank.currency_id == currency_id:
                    bank_name = bank.currency_id.name
                    account_number = bank.acc_number
                    bank_bic = bank.bank_bic
                    if bank_type:
                        if bank.bank_id.id == bank_type.id:
                            break
                        else:
                            bank_name = bank.currency_id.name
                            account_number = bank.acc_number
                            bank_bic = bank.bank_bic


        for line in order_lines:
            if line.analytic_distribution:
                analytic_distribution_id = list(line.analytic_distribution.keys())[0]
                if analytic_distribution_id != 'False':
                    analytic_account = self.env['account.analytic.account'].search([('id', '=', analytic_distribution_id)])
                    if analytic_account:
                        name = analytic_account.name
                        name = name.split('-')[0] + '-' + name.split('-')[1]
                        if name not in analytic_distribution_names:
                            analytic_distribution_names.append(name)

        return {
            'doc_ids': docids,
            'doc_model': 'purchase.order',
            'docs': docs,
            'analytic_distribution_names': ', '.join(name for name in analytic_distribution_names ),
            'bank_name': bank_name,
            'account_number': account_number,
            'bank_bic': bank_bic,
        }