from odoo import models, fields

import base64

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

    # CRON: ir_cron_create_purchase_order_from_preorder
    def create_purchase_order_from_products(self, products):
        po_lines = []
        for product in products:
            po_lines.append([0, 0, {
                'name': product.get("name"),
                'product_id': product.get("id"),
                'product_qty': product.get("qty"),
                'product_uom': product.get("uom"),
                'date_planned': fields.Date.context_today(self),
                'price_unit': 0,
                'taxes_id': product.get("taxes_id"),
            }])
        po_id = self.create({
            'partner_id': self.env.user.company_id.partner_id.id,
            'order_line': po_lines
        })
        po_id.message_post(body="Creado desde Pre-ordenes de Compra mediante Acción Automática.")

    def __separate_categories_with_products(self, items):
        categories = dict()
        for products in items.values():
            for product in products:
                product_data = {
                    'name': product.get("name"),
                    'id': product.get("id"),
                    'qty': product.get("qty"),
                    'uom': product.get("uom"),
                    'taxes_id': [(6, 0, product.get("taxes_id"))],
                }
                category_id = product.get("category_id")
                if not category_id in categories:
                    categories.update({
                        category_id: []
                    })
                prod = next((prod for prod in categories[category_id] if prod["id"] == product_data.get("id")), None)
                if prod:
                    prod.update({
                        "qty": prod.get("qty") + product_data.get("qty")
                    })
                else:
                    categories[category_id].append(product_data)
        return categories

    def _calculate_product_stock_from_location(self, location_id, products):
        for product in products:
            quant_id = self.env['stock.quant'].search([('product_id', '=', product.get("id")), ('location_id', '=', location_id)], limit=1)
            stock_qty = quant_id.quantity if quant_id else 0
            product_stock_uom = quant_id.product_uom_id.id if quant_id else product.get("uom")
            
            if not product_stock_uom == product.get("uom"):
                products.remove(product)
            else:
                new_qty = product.get("qty") - stock_qty
                if new_qty <= 0:
                    products.remove(product)
                else:
                    product.update({
                        "qty": new_qty
                    })
        return products

    def __check_product_stock(self, items):
        for loc_id, products in items.items():
            products = self._calculate_product_stock_from_location(loc_id, products)
        items = self.__separate_categories_with_products(items)
        principal_warehouse_id = self.env["stock.location"].search([('complete_name', '=', 'A-AQP/Stock')])
        for products in items.values():
            products = self._calculate_product_stock_from_location(principal_warehouse_id.id, products)
        return items

    def _separate_products_from_preorders(self, preorder_ids):
        locations = dict()
        for preorder_id in preorder_ids:
            location_id = preorder_id.location_id.id
            if not location_id in locations:
                products = list()
            else:
                products = locations.get(location_id)

            for line_id in preorder_id.line_ids:
                    product = next((product for product in products if product["id"] == line_id.product_id.id), None)
                    if product:
                        product.update({
                            "qty": product.get("qty") + line_id.product_qty
                        })
                    else:
                        products.append({
                            "id": line_id.product_id.id,
                            'name': line_id.product_id.display_name,
                            "qty": line_id.product_qty,
                            "uom": line_id.product_uom.id,
                            "category_id": line_id.product_id.categ_id.id,
                            "taxes_id": line_id.product_id.supplier_taxes_id.ids,
                        })
            locations.update({
                location_id: products
            })
        return locations

    def create_purchase_order_from_preorder(self):
        preorder_ids = self.env["purchase.preorder"].search([('state', '=', 'preorder'), ('check_po_generated', '=', False)])
        locations_prods = self._separate_products_from_preorders(preorder_ids)
        categories_prods = self.__check_product_stock(locations_prods)
        for products in categories_prods.values():
            if len(products):
                self.create_purchase_order_from_products(products)

        for preorder_id in preorder_ids:
            preorder_id.write({
                "check_po_generated": True
            })
