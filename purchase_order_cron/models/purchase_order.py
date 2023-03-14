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

    # CRON: ir_cron_create_purchase_order_from_preorder
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
        product_liens = dict()
        for line in self.order_line:
            if not product_liens.get(line.product_id.id, False):
                product_liens[line.product_id.id] = {
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
                product_liens[line.product_id.id]['product_qty'] += round(line.product_qty, 3)
        return [value for value in product_liens.values()]

    def _create_purchase_order_from_products(self, products):
        po_lines = []
        for product in products:
            po_lines.append([0, 0, {
                'name': product["product_name"],
                'product_id': product["product_id"],
                'product_qty': product["product_qty"],
                'product_uom': product["product_uom"],
                'analytic_distribution': product["product_analytic_distribution"],
                'date_planned': fields.Date.context_today(self),
                'price_unit': 0,
                'taxes_id': product["product_taxes_id"],
            }])
        po_id = self.create({
            'partner_id': self.env.user.company_id.partner_id.id,
            'order_line': po_lines
        })
        po_id.message_post(body="Creado desde Pre-ordenes de Compra mediante Acción Automática.")

    def _separate_products_by_categories(self, products):
        """
            Se crea una diccionario con los productos separados por categoría.

            Args:
                - products: list

            Return:
                - categories_prods: dict
        """
        categories_prods = dict()
        for product in products:
            categ_id = product["product_categ_id"]
            project_id = product["project_id"]
            product_id = product["product_id"]
            if categ_id not in categories_prods:
                categories_prods.update({
                    categ_id: [product]
                })
            else:
                prod = next((prod for prod in categories_prods[categ_id] if prod["project_id"] == project_id), None)
                if prod:
                    prod["product_qty"] += product["product_qty"]
                else:
                    categories_prods[categ_id].append(product)
        return categories_prods

    def _subtract_stock_from_warehouse(self, product_id, product_qty, stocks, location_id):
        """
            Dado un el id y la cantidad de un producto, el objeto de stocks y el almacén, se realiza el
            cálculo de la nueva cantidad del producto y lo restante en el almacén.

            Args:
                - product_id:   int
                - product_qty:  float
                - stocks:       dict
                - location_id:  int

            Return:
                - product_qty:  float
                - stocks:       dict
        """
        if stocks[location_id][product_id] and product_qty:
            res = stocks[location_id][product_id] - product_qty
            if not res:
                product_qty = 0
                stocks[location_id][product_id] = 0
            elif res > 0:
                product_qty = 0
                stocks[location_id][product_id] = res
            else:
                product_qty = abs(res)
                stocks[location_id][product_id] = 0
        return product_qty, stocks

    def _update_product_stock_warehouse(self, preorder_ids, stocks_project_warehouse, stock_principal_warehouse):
        """
            Se crea una lista con los productos con los stocks actualizados
            respecto a los almacenes de los proyectos y del almacén principal,
            eliminando los productos que no tengan cantidad mayor a 0.

            Args:
                - preorder_ids: object(purchase_preorder)
                - stocks_project_warehouse: dict
                - stock_principal_warehouse: dict

            Return:
                - products: list
        """
        products = list()
        principal_warehouse_id = self.env["stock.location"].search([('complete_name', '=', 'A-AQP/Stock')], limit=1).id
        for preorder_id in preorder_ids:
            analytic_account_id = preorder_id.project_id.analytic_account_id.id
            location_id = preorder_id.location_id.id
            for line_id in preorder_id.line_ids:
                product_id = line_id.product_id.id
                product_qty = line_id.product_qty
                product_qty, stocks_project_warehouse = self._subtract_stock_from_warehouse(product_id, product_qty, stocks_project_warehouse, location_id)
                product_qty, stock_principal_warehouse = self._subtract_stock_from_warehouse(product_id, product_qty, stock_principal_warehouse, principal_warehouse_id)

                products.append({
                    "product_categ_id": line_id.product_id.categ_id.id,
                    "project_id": preorder_id.project_id.id,
                    "product_id": product_id,
                    "product_name": line_id.product_id.display_name,
                    "product_qty": product_qty,
                    "product_analytic_distribution": {str(analytic_account_id): 100.0},
                    "product_uom": line_id.product_uom.id,
                    "product_taxes_id": line_id.product_id.supplier_taxes_id.ids,
                })
        return [prod for prod in products if prod["product_qty"] > 0]

    def _get_stocks_warehouse_from_preorders(self, preorder_ids):
        """
            Se construyen dos diccionarios, un diccionara para los stocks de productos en el almacen principal
            y otro diccionario para los stocks de los productos en los almacenes de proyectos. La estructura de
            los diccionarios es la siguiente:
            {
                location_id: {
                    product_id: stock,
                    ...
                },
                ...
            }

            Args:
                - preorder_ids: object(purchase_preorder)

            Return:
                - warehouses: dict
                - principal_warehouse: dict
        """
        warehouses = dict()
        principal_warehouse_id = self.env["stock.location"].search([('complete_name', '=', 'A-AQP/Stock')], limit=1).id
        principal_warehouse = {
            principal_warehouse_id: dict()
        }
        for preorder_id in preorder_ids:
            location_id = preorder_id.location_id.id
            if location_id not in warehouses:
                warehouses.update({
                    location_id: dict()
                })
            for line_id in preorder_id.line_ids:
                product_id = line_id.product_id.id
                if product_id not in warehouses[location_id]:
                    quant_id = self.env['stock.quant'].search([('product_id', '=', product_id), ('location_id', '=', location_id)], limit=1)
                    stock_qty = quant_id.quantity if quant_id else 0
                    warehouses[location_id].update({
                        product_id: stock_qty
                    })
                if product_id not in principal_warehouse[principal_warehouse_id]:
                    quant_id = self.env['stock.quant'].search([('product_id', '=', product_id), ('location_id', '=', principal_warehouse_id)], limit=1)
                    stock_qty = quant_id.quantity if quant_id else 0
                    principal_warehouse[principal_warehouse_id].update({
                        product_id: stock_qty
                    })
        return warehouses, principal_warehouse
        
    def create_purchase_order_from_preorder(self):
        preorder_ids = self.env["purchase.preorder"].search([('state', '=', 'preorder'), ('check_po_generated', '=', False)], order="date_order asc")
        stocks_project_warehouse, stock_principal_warehouse = self._get_stocks_warehouse_from_preorders(preorder_ids)
        products = self._update_product_stock_warehouse(preorder_ids, stocks_project_warehouse, stock_principal_warehouse)
        categories_prods = self._separate_products_by_categories(products)
        for products in categories_prods.values():
            self._create_purchase_order_from_products(products)

        for preorder_id in preorder_ids:
            preorder_id.write({
                "check_po_generated": True
            })