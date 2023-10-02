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
        data = self.get_data(data['project_id'])
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

        sheet.merge_range('A2:B2', 'Proyecto: ', formats['bold_center'])
        if len(data) > 0:
            sheet.merge_range('C2:G2', data[0].get('name_project').get(user_lang, ''), formats['normal_left'])

        sheet.set_column('A:A', 5)
        sheet.set_column('B:B', 15)
        sheet.set_column('C:C', 15)
        sheet.set_column('D:D', 10)
        sheet.set_column('E:E', 60)
        sheet.set_column('F:F', 10)
        sheet.set_column('G:G', 10)
        sheet.set_column('H:H', 10)
        sheet.set_column('I:I', 10)
        sheet.set_column('J:J', 10)
        sheet.set_column('K:K', 10)
        sheet.set_column('L:L', 30)
        sheet.set_column('M:M', 15)
        sheet.set_column('N:N', 10)
        sheet.set_column('O:O', 15)
        sheet.set_column('P:P', 20)

        
        row_header= 3
       
        sheet.write(row_header, 1, 'Nro de Pre-Orden', formats['bold_center'])
        sheet.write(row_header, 2, 'Fecha de Pre-Orden', formats['bold_center'])
        # sheet.write(row_header, 3, 'Proyecto', formats['bold_center'])
        sheet.write(row_header, 3, 'Codigo', formats['bold_center'])
        sheet.write(row_header, 4, 'Material', formats['bold_center'])
        sheet.write(row_header, 5, 'Unidad', formats['bold_center'])
        sheet.write(row_header, 6, 'Cantidad pedida', formats['bold_center'])
        sheet.write(row_header, 7, 'Cantidad atendida', formats['bold_center'])
        sheet.write(row_header, 8, 'Materiales con stock', formats['bold_center'])
        sheet.write(row_header, 9, 'Materiales comprados', formats['bold_center'])
        sheet.write(row_header, 10, 'Orden de Compra', formats['bold_center'])
        sheet.write(row_header, 11, 'Proveedor', formats['bold_center'])
        sheet.write(row_header, 12, 'Precio Unitario', formats['bold_center'])
        sheet.write(row_header, 13, 'Monto sin IGV', formats['bold_center'])
        sheet.write(row_header, 14, 'Moneda', formats['bold_center'])
        sheet.write(row_header, 15, 'Fecha de Compra', formats['bold_center'])
        sheet.write(row_header, 16, 'Usuario Emisor', formats['bold_center'])

        row = 4
        if len(data) > 0:
            for item in data:
                sheet.write(row, 1, item['name'], formats['normal_center'])
                sheet.write(row, 2, item['date_order'], formats['date_format'])
                # sheet.write(row, 3, item.get('name_project').get(user_lang, ''), formats['normal_left'])
                sheet.write(row, 3, item['codigo_material'], formats['normal_center'])
                sheet.write(row, 4, item.get('nombre_material').get(user_lang, ''), formats['normal_left'])
                sheet.write(row, 5, item.get('unidadmedida').get(user_lang, ''), formats['normal_center'])

                sheet.write(row, 6, item['cantidad_pedida'], formats['normal_center'])
                sheet.write(row, 7, item['cantidad_atendida'], formats['normal_center'])
                sheet.write(row, 8, item['materiale_stock'], formats['normal_center'])
                materiales_comprados = int(item['cantidad_pedida']) - int(item['materiale_stock']) 
                sheet.write(row, 9, materiales_comprados if materiales_comprados > 0 else 0, formats['normal_center'])

                sheet.write(row, 10, item['name_purchase_order'], formats['normal_center'])
                sheet.write(row, 11, item['name_proveedor'], formats['normal_left'])
                sheet.write(row, 12, self.get_unit_price_from_product(item['id_product']), formats['normal_center'])
                sheet.write(row, 13, item['monto_sin_igv'], formats['normal_center'])
                sheet.write(row, 14, item['tipo_moneda'], formats['normal_center'])
                sheet.write(row, 15, item['fecha_compra'], formats['date_format'])
                sheet.write(row, 16, item['usuario_emisor'], formats['normal_center'])
                row += 1
        else:
            sheet.write(row, 0, 'NO HAY DATOS / REPORTE EN CONSTRUCCION', )

    def get_unit_price_from_product(self, product_id):
        product = self.env['product.template'].browse(product_id)
        standard_price = product.standard_price
        return standard_price if standard_price else 0

    def get_data(self, id):
        query = """
            (SELECT
                pp.name,
                pp.date_order,
                pp2.name as name_project,
                po.name name_purchase_order,
                rp.name as name_proveedor,
                pol.price_subtotal as monto_sin_igv,
                rc.name as tipo_moneda,
                po.date_approve as fecha_compra,
                rp2.name as usuario_emisor,
                ppl.product_qty as cantidad_pedida,
                pol.product_qty as cantidad_atendida,
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
                pp.project_id = %s)

            UNION ALL

            (SELECT
                pp.name,
                pp.date_order,
                pp2.name as name_project,
                NULL name_purchase_order,
                NULL as name_proveedor,
                NULL as monto_sin_igv,
                NULL as tipo_moneda,
                NULL as fecha_compra,
                NULL as usuario_emisor,
                ppl.product_qty as cantidad_pedida,
                NULL as cantidad_atendida,
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
                pp.project_id = %s
                AND NOT EXISTS (
                    SELECT 1
                    FROM purchase_order po
                    INNER JOIN purchase_order_line pol ON pol.order_id = po.id
                    WHERE po.from_preorders = pp.name AND pol.product_id = ppl.product_id))

            ORDER BY name_project desc;
        """ % (id, id)

        self.env.cr.execute(query)
        return self.env.cr.dictfetchall()