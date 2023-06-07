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

        formats = {
            'bold_center': workbook.add_format({'bold': True, 'align': 'center', 'valign': 'vcenter', 'text_wrap': True}),
            'bold_right': workbook.add_format({'bold': True, 'align': 'right'}),
            'normal_center': workbook.add_format({'align': 'center'}),
            'normal_right': workbook.add_format({'align': 'right'}),
            'normal_left': workbook.add_format({'align': 'left'}),
            'date_format': workbook.add_format({'num_format': 'dd/mm/yyyy', 'align': 'center'}),
        }
        sheet.merge_range('A1:G1', 'REPORTE DE PRE-ORDENES POR PROYECTO', formats['bold_center'])

        sheet.set_column('A:A', 5)
        sheet.set_column('B:B', 15)
        sheet.set_column('C:C', 15)
        sheet.set_column('D:D', 50)
        sheet.set_column('E:E', 10)
        sheet.set_column('F:F', 10)
        sheet.set_column('G:G', 10)
        sheet.set_column('H:H', 10)
        sheet.set_column('I:I', 15)
        sheet.set_column('J:J', 40)
        sheet.set_column('K:K', 13)
        sheet.set_column('L:L', 10)
        sheet.set_column('M:M', 15)
        sheet.set_column('N:N', 15)
        
        row_header= 2
       
        sheet.write(row_header, 1, 'Nro de Pre-Orden', formats['bold_center'])
        sheet.write(row_header, 2, 'Fecha de Pre-Orden', formats['bold_center'])
        sheet.write(row_header, 3, 'Proyecto', formats['bold_center'])
        sheet.write(row_header, 4, 'Cantidad pedida', formats['bold_center'])
        sheet.write(row_header, 5, 'Cantidad atendida', formats['bold_center'])
        sheet.write(row_header, 6, 'Materiales atendidos', formats['bold_center'])
        sheet.write(row_header, 7, 'Materiales comprados', formats['bold_center'])
        sheet.write(row_header, 8, 'Orden de Compra', formats['bold_center'])
        sheet.write(row_header, 9, 'Proveedor', formats['bold_center'])
        sheet.write(row_header, 10, 'Monto sin IGV', formats['bold_center'])
        sheet.write(row_header, 11, 'Moneda', formats['bold_center'])
        sheet.write(row_header, 12, 'Fecha de Compra', formats['bold_center'])
        sheet.write(row_header, 13, 'Usuario Emisor', formats['bold_center'])

        row = 3
        if len(data) > 0:
            for item in data:
                sheet.write(row, 1, item['name'], formats['normal_center'])
                sheet.write(row, 2, item['date_order'], formats['date_format'])
                sheet.write(row, 3, item.get('name_project').get('es_PE', ''), formats['normal_left'])
                sheet.write(row, 4, item['cantidad_pedida'], formats['normal_center'])
                sheet.write(row, 5, item['cantidad_stock'], formats['normal_center'])
                sheet.write(row, 6, item['cantidad_stock'], formats['normal_center'])
                sheet.write(row, 7, item['materiales_comprados'], formats['normal_center'])
                sheet.write(row, 8, item['name_purchase_order'], formats['normal_center'])
                sheet.write(row, 9, item['name_proveedor'], formats['normal_left'])
                sheet.write(row, 10, item['monto_sin_igv'], formats['normal_center'])
                sheet.write(row, 11, item['tipo_moneda'], formats['normal_center'])
                sheet.write(row, 12, item['fecha_compra'], formats['date_format'])
                sheet.write(row, 13, item['usuario_emisor'], formats['normal_center'])
                row += 1
        else:
            sheet.write(row, 0, 'NO HAY DATOS / REPORTE EN CONSTRUCCION', )

    def get_data(self, id):
        query = """
            select 
                pp.name, 
                pp.date_order, 
                pp2.name as name_project,
                po.name name_purchase_order,
                rp.name as name_proveedor, 
                po.amount_untaxed as monto_sin_igv,
                rc.name as tipo_moneda, 
                po.date_approve as fecha_compra, 
                rp2.name as usuario_emisor,
                sum(ppl.product_qty) as cantidad_pedida,
                sum(ppl.stock_qty) as cantidad_stock,
                sum(ppl.purchase_product_qty) as materiales_comprados
            from 
                purchase_preorder pp
                left join project_project pp2 on pp2.id = pp.project_id
                left join purchase_order po on po.from_preorders = pp.name
                left join res_partner rp on po.partner_id = rp.id
                left join res_currency rc on po.currency_id = rc.id
                left join res_users ru on po.user_id = ru.id
                left join res_partner rp2 on ru.partner_id = rp2.id
                left join purchase_preorder_line ppl on ppl.preorder_id = pp.id
            where 
                pp.state = 'preorder'
                and pp.po_state = 'generate'
                --and po.state = 'purchase'
                and pp2.id = %s
            group by 
                pp.name, pp.date_order, pp2.name, rp.name, po.amount_untaxed, rc.name, po.date_approve, rp2.name, po.name
            order by 
	            pp2.name desc   
        """ % (id)

        self.env.cr.execute(query)
        return self.env.cr.dictfetchall()