from odoo import models, api, fields, _
from datetime import datetime
import logging
log = logging.getLogger(__name__)

class ReportPreorderProject(models.AbstractModel):
    _name = 'report.report_preorders_project.report_preorder_project_xlsx'
    _inherit = 'report.report_xlsx.abstract'
    _description = 'Reporte de pre-ordenes por proyecto'

    def generate_xlsx_report(self, workbook, data, lines):
        sheet = workbook.add_worksheet('Reporte de pre-ordenes por proyecto')
        from_date = data['from_date']
        to_date = data['to_date']
        data = self.get_data(from_date + " 00:00:00", to_date + " 23:59:59")
        user_lang = self.env.user.lang

        formats = {
            'bold_center': workbook.add_format({'bold': True, 'align': 'center', 'valign': 'vcenter', 'text_wrap': True}),
            'bold_right': workbook.add_format({'bold': True, 'align': 'right'}),
            'normal_center': workbook.add_format({'align': 'center'}),
            'normal_right': workbook.add_format({'align': 'right'}),
            'normal_left': workbook.add_format({'align': 'left'}),
            'date_format': workbook.add_format({'num_format': 'dd/mm/yyyy', 'align': 'center'}),
        }
        sheet.merge_range('A1:G1', 'REPORTE DE PRE-ORDENES POR PROYECTO', formats['bold_center'])

        sheet.write(1, 1, 'Desde:', formats['bold_right'])
        sheet.write(1, 2, from_date, formats['date_format'])
        sheet.write(2, 1, 'Hasta:', formats['bold_right'])
        sheet.write(2, 2, to_date, formats['date_format'])

        sheet.set_column('A:A', 5)
        sheet.set_column('B:B', 15)
        sheet.set_column('C:C', 15)
        sheet.set_column('D:D', 25)
        sheet.set_column('E:E', 10)
        sheet.set_column('F:F', 60)
        sheet.set_column('G:G', 10)
        sheet.set_column('H:H', 10)
        sheet.set_column('I:I', 10)
        sheet.set_column('J:J', 10)
        sheet.set_column('K:K', 10)
        sheet.set_column('L:L', 10)
        sheet.set_column('M:M', 30)
        sheet.set_column('N:N', 15)
        sheet.set_column('O:O', 10)
        sheet.set_column('P:P', 15)
        sheet.set_column('Q:Q', 20)
        sheet.set_column('R:R', 15)

        
        row_header= 4
       
        sheet.write(row_header, 1, 'Nro de Pre-Orden', formats['bold_center'])
        sheet.write(row_header, 2, 'Fecha de Pre-Orden', formats['bold_center'])
        sheet.write(row_header, 3, 'Proyecto', formats['bold_center'])
        sheet.write(row_header, 4, 'Codigo', formats['bold_center'])
        sheet.write(row_header, 5, 'Material', formats['bold_center'])
        sheet.write(row_header, 6, 'Unidad', formats['bold_center'])
        sheet.write(row_header, 7, 'Cantidad pedida', formats['bold_center'])
        sheet.write(row_header, 8, 'Cantidad atendida', formats['bold_center'])
        sheet.write(row_header, 9, 'Materiales con stock', formats['bold_center'])
        sheet.write(row_header, 10, 'Materiales comprados', formats['bold_center'])
        sheet.write(row_header, 11, 'Orden de Compra', formats['bold_center'])
        sheet.write(row_header, 12, 'Proveedor', formats['bold_center'])
        sheet.write(row_header, 13, 'Precio Unitario sin IGV', formats['bold_center'])
        sheet.write(row_header, 14, 'Monto sin IGV', formats['bold_center'])
        sheet.write(row_header, 15, 'Moneda', formats['bold_center'])
        sheet.write(row_header, 16, 'Fecha de Compra', formats['bold_center'])
        sheet.write(row_header, 17, 'Usuario Emisor', formats['bold_center'])

        row = 5
        if len(data) > 0:
            for item in data:
                sheet.write(row, 1, item['name'], formats['normal_center'])
                sheet.write(row, 2, item['date_order'], formats['date_format'])
                log.info(item)
                sheet.write(row, 3, item.get('name_project').get(user_lang, ''), formats['normal_left'])
                sheet.write(row, 4, item['codigo_material'], formats['normal_center'])

                nombre_material = item.get('nombre_material')
                unidadmedida = item.get('unidadmedida')
                if nombre_material:
                    sheet.write(row, 5, nombre_material.get(user_lang, ''), formats['normal_left'])
                else:
                    sheet.write(row, 5, '', formats['normal_left'])

                if unidadmedida:
                    sheet.write(row, 6, unidadmedida.get(user_lang, ''), formats['normal_center'])
                else:
                    sheet.write(row, 6, '', formats['normal_center'])

                sheet.write(row, 7, item['cantidad_pedida'], formats['normal_center'])
                sheet.write(row, 8, item['cantidad_atendida'], formats['normal_center'])
                sheet.write(row, 9, item['materiale_stock'], formats['normal_center'])
                
                cantidad_pedida = item.get('cantidad_pedida') or 0
                materiale_stock = item.get('materiale_stock') or 0

                materiales_comprados = int(cantidad_pedida) - int(materiale_stock)

                sheet.write(row, 10, materiales_comprados if materiales_comprados > 0 else 0, formats['normal_center'])

                sheet.write(row, 11, item['name_purchase_order'], formats['normal_center'])
                sheet.write(row, 12, item['name_proveedor'], formats['normal_left'])
                sheet.write(row, 13, item['precio_unitario'], formats['normal_center'])
                sheet.write(row, 14, item['monto_sin_igv'], formats['normal_center'])
                sheet.write(row, 15, item['tipo_moneda'], formats['normal_center'])
                sheet.write(row, 16, item['fecha_compra'], formats['date_format'])
                sheet.write(row, 17, item['usuario_emisor'], formats['normal_center'])
                row += 1
        else:
            sheet.write(row, 0, 'NO HAY DATOS / REPORTE EN CONSTRUCCION', )

    def get_unit_price_from_product(self, product_id):
        product = self.env['product.template'].browse(product_id)
        standard_price = product.standard_price
        return standard_price if standard_price else 0

    def get_data(self, from_date, to_date):
        query = """
            (SELECT
                pp.name,
                pp.date_order as date_order,
                pp2.name as name_project,
                po.name name_purchase_order,
                po.id as id_purchase_order,
                rp.name as name_proveedor,
                pol.price_subtotal as monto_sin_igv,
                rc.name as tipo_moneda,
                po.date_approve as fecha_compra,
                rp2.name as usuario_emisor,
                ppl.product_qty as cantidad_pedida,
                pol.product_qty as cantidad_atendida,
                pol.price_unit as precio_unitario,
                ppl.stock_qty as materiale_stock,
                pt."name" as nombre_material,
                pt.default_code as codigo_material,
                uu.name as unidadmedida,
                pt.id as id_product
            FROM
                purchase_preorder pp
                LEFT JOIN project_project pp2 ON pp2.id = pp.project_id
                LEFT JOIN purchase_preorder_line ppl ON ppl.preorder_id = pp.id
                LEFT JOIN purchase_order po ON po.from_preorders = pp.name
                INNER JOIN purchase_order_line pol ON pol.order_id = po.id AND pol.product_id = ppl.product_id
                LEFT JOIN res_partner rp ON po.partner_id = rp.id
                LEFT JOIN res_currency rc ON po.currency_id = rc.id
                LEFT JOIN res_users ru ON po.user_id = ru.id
                LEFT JOIN res_partner rp2 ON ru.partner_id = rp2.id
                INNER JOIN product_product pp3 ON ppl.product_id = pp3.id
                LEFT JOIN product_template pt ON pt.id = pp3.product_tmpl_id
                LEFT JOIN uom_uom uu ON pt.uom_id = uu.id
            WHERE
                pp.date_order >= '%s'
                AND pp.date_order <= '%s')

            UNION ALL

            (SELECT
                pp.name,
                pp.date_order as date_order,
                pp2.name as name_project,
                NULL name_purchase_order,
                NULL as id_purchase_order,
                NULL as name_proveedor,
                NULL as monto_sin_igv,
                NULL as tipo_moneda,
                NULL as fecha_compra,
                NULL as usuario_emisor,
                ppl.product_qty as cantidad_pedida,
                NULL as cantidad_atendida,
                NULL as precio_unitario,
                ppl.stock_qty as materiale_stock,
                pt."name" as nombre_material,
                pt.default_code as codigo_material,
                uu.name as unidadmedida,
                pt.id as id_product
            FROM
                purchase_preorder pp
                LEFT JOIN project_project pp2 ON pp2.id = pp.project_id
                LEFT JOIN purchase_preorder_line ppl ON ppl.preorder_id = pp.id
                LEFT JOIN product_product pp3 ON ppl.product_id = pp3.id
                LEFT JOIN product_template pt ON pt.id = pp3.product_tmpl_id
                LEFT JOIN uom_uom uu ON pt.uom_id = uu.id
            WHERE
                pp.date_order >= '%s'
                AND pp.date_order <= '%s'
                AND NOT EXISTS (
                    SELECT 1
                    FROM purchase_order po
                    INNER JOIN purchase_order_line pol ON pol.order_id = po.id
                    WHERE po.from_preorders = pp.name AND pol.product_id = ppl.product_id))

            ORDER BY date_order ASC, name_project ASC;
        """ % (from_date, to_date, from_date, to_date)

        log.info(query)

        self.env.cr.execute(query)
        return self.env.cr.dictfetchall()