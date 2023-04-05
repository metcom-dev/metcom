from odoo import models, fields

import base64
from datetime import datetime, timedelta

import logging
log = logging.getLogger(__name__)

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    # CRON: ir_cron_autosend_purchase_quotation_suppliers
    def process_send_quotation_suppliers(self):
        order_ids = self.env['purchase.order'].search([('state', '=', 'draft'), ('company_id', '=', self.env.company.id)])
        for order_id in order_ids:
            pdf = self.env['ir.actions.report']._render_qweb_pdf('purchase.report_purchasequotation', [order_id.id])
            
            att = self.env['ir.attachment'].create({
                'name': 'RFQ_%s.pdf' % (order_id.name),
                'type': 'binary',
                'datas': base64.encodebytes(pdf[0]),
                'res_model': 'account.invoice',
                'mimetype': 'application/x-pdf'
            })
            for line_id in order_id.order_line:
                if line_id.product_id.categ_id.supplier_ids:
                    for supplier_id in line_id.product_id.categ_id.supplier_ids:
                        mail_vals = {
                            'subject': '%s - Solicitud de Presupuesto Ref (%s)' % (self.env.company.name, order_id.name),
                            'email_to': supplier_id.email,
                            'auto_delete': True,
                            'message_type':'email',
                            'body_html': """
                                <div style="margin: 0px; padding: 0px;">
                                \n    <p style="margin: 0px; padding: 0px; font-size: 13px;">
                                \n        Apreciable %s
                                \n        <br/><br/>
                                \n        Adjuntamos la solicitud de cotización <span style="font-weight:bold;">%s</span>
                                \n        de %s.
                                \n        <br/><br/>
                                \n        Si tiene preguntas no dude en contactarnos.
                                \n        <br/><br/>
                                \n        Saludos,
                                \n            <br/><br/>
                                \n            <span data-o-mail-quote="1">-- <br data-o-mail-quote="1">
                                \nAdministrator</span>
                                \n    </p>
                                \n</div>""" % (supplier_id.name, order_id.name, self.env.company.name),
                            'attachment_ids': [(6, 0, [att.id])]
                        }
                        mail_id = self.env['mail.mail'].sudo().create(mail_vals).send()
                        order_id.write({'state': 'sent'})

    def _get_quotation_new_order_lines(self):
        product_liens = dict()
        for line in self.order_line:
            if not product_liens.get(line.product_id.id, False):
                product_liens[line.product_id.id] = {
                    "display_type": line.display_type,
                    "name": line.name,
                    "date_planned": datetime.strftime(line.date_planned - timedelta(hours=5), '%d/%m/%Y %H:%M:%S'),
                    "product_qty": line.product_qty,
                    "product_uom": line.product_uom,
                }
            else:
                product_liens[line.product_id.id]['product_qty'] += round(line.product_qty, 3)
        return [value for value in product_liens.values()]

    def _get_order_new_order_lines(self):
        product_lines = dict()
        for line in self.order_line:
            if not product_lines.get(line.product_id.id, False):
                product_lines[line.product_id.id] = {
                    "price_subtotal": line.price_subtotal,
                    "price_total": line.price_total,
                    "display_type": line.display_type,
                    "name": line.name,
                    "taxes_id": line.taxes_id,
                    "date_planned": datetime.strftime(line.date_planned - timedelta(hours=5), '%d/%m/%Y %H:%M:%S'),
                    "product_qty": line.product_qty,
                    "product_uom": line.product_uom,
                    "price_unit": line.price_unit,
                }
            else:
                product_lines[line.product_id.id]['product_qty'] += round(line.product_qty, 3)
        return [value for value in product_lines.values()]