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
