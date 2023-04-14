from odoo import api, models, fields

import logging
log = logging.getLogger(__name__)

class ReportPurchaseOrder(models.AbstractModel):
    _name = 'report.purchase.report_purchaseorder'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['purchase.order'].browse(docids)
        order_lines = docs.order_line
        analytic_distribution_names = []

        for line in order_lines:
            if line.analytic_distribution:
                analytic_distribution_id = list(line.analytic_distribution.keys())[0]
                if analytic_distribution_id != 'False':
                    analytic_account = self.env['account.analytic.account'].search([('id', '=', analytic_distribution_id)])
                    if analytic_account:
                        if analytic_account.name not in analytic_distribution_names:
                            analytic_distribution_names.append(analytic_account.name)

        return {
            'doc_ids': docids,
            'doc_model': 'purchase.order',
            'docs': docs,
            'analytic_distribution_names': analytic_distribution_names,
        }
        