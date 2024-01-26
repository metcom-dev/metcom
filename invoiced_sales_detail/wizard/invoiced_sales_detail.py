# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime
#report_invoiced_sales_detail
import logging
log = logging.getLogger(__name__)


class InvoicedSalesDetail(models.TransientModel):
    _name = 'report.invoiced_sales_detail'
    _description = 'invoiced sales detail'

    company_id = fields.Many2one('res.company', string='Compañia', default=lambda self: self.env.company.id)
    # company_branch_address_ids = fields.Many2many(string='Sucursales', comodel_name='res.company.branch.address')
    date_from = fields.Date(string='Desde', default=fields.Date.context_today)
    date_to = fields.Date(string='Hasta', default=fields.Date.context_today)
    # show_branch_field = fields.Boolean(compute='_compute_show_branch_field')

    # @api.depends('company_id')
    # def _compute_show_branch_field(self):
    #     for record in self:
    #         branches = self.env['res.company.branch.address'].search_count([('company_id', '=', record.company_id.id)])
    #         record.show_branch_field = branches > 1

    def print_report(self, data=None):
        return {
            'type': 'ir.actions.report',
            'report_name': 'invoiced_sales_detail.invoiced_sales_detail_xls.xlsx',
            'report_type': 'xlsx',
            'lines': self,
        }

    def get_data(self):
        self.ensure_one()
        # branches = self.env['res.company.branch.address'].search_count([('company_id', '=', self.company_id.id)])
        # sql_branch = ''
        # if self.company_branch_address_ids:
        #     if len(self.company_branch_address_ids) != branches: 
        #         sql_branch = 'AND ai.company_branch_address_id IN (%s)' % ','.join(map(str,self.company_branch_address_ids.ids))

        sql_ext = ""
        if False:
            #variable para integraciones
            sql_ext = ""
        else:
            sql_ext = "INNER JOIN l10n_latam_document_type AS ajd ON ajd.id = ai.l10n_latam_document_type_id"

        query = """
            SELECT ail.name ail_name, pu.name uom, ail.price_unit, ail.quantity, ajd.code code_journal, 
                ai.name ai_number, ai.invoice_date
            FROM account_move_line ail
            INNER JOIN account_move ai ON ai.id = ail.move_id
            %s
            INNER JOIN uom_uom pu ON pu.id = ail.product_uom_id
            WHERE ai.move_type= 'out_invoice'
                AND ai.company_id = %s
                AND ai.invoice_date >= '%s'
                AND ai.invoice_date <= '%s'
                AND ai.state IN ('posted')
            ORDER BY ai.invoice_date, ai.name""" % (sql_ext, self.company_id.id, self.date_from, self.date_to)
        log.info("query: %s" % query)
        self.env.cr.execute(query)

        return self.env.cr.dictfetchall()


class InvoicedSalesDetailReportXlsx(models.AbstractModel):
    _name = 'report.invoiced_sales_detail.invoiced_sales_detail_xls.xlsx'
    _inherit = 'report.report_xlsx.abstract'
    _description = 'invoiced sales detail report xlsx'

    def generate_xlsx_report(self, workbook, data, lines):
        wizard = lines[0]
        _data = wizard.get_data()

        # get language code from user
        lang_code = self.env.user.lang

        sheet = workbook.add_worksheet('DETALLE')
        sheet.set_column('A:A', 10)
        sheet.set_column('B:B', 65)
        sheet.set_column('C:F', 13)
        sheet.set_column('F:I', 16)
        formats = {
            'title': workbook.add_format({'bold': True, 'align': 'center', 'font_size': 18}),
            'bold': workbook.add_format({'bold': True}),
            'header': workbook.add_format({'bold': True, 'align': 'center', 'border': 1}),
            'normal_center': workbook.add_format({'align': 'center', 'border': 1}),
            'normal_left': workbook.add_format({'align': 'left', 'border': 1}),
            'format_number': workbook.add_format({'align': 'right', 'num_format': '0.00', 'border': 1}),
            'format_qty': workbook.add_format({'align': 'center', 'num_format': '0.0', 'border': 1})
        }

        sheet.merge_range('A1:I1', 'REPORTE DE VENTAS DETALLADAS', formats['title'])
        sheet.write(2, 0, 'Empresa:', formats['bold'])
        sheet.write(2, 1, wizard.company_id.name, )
        sheet.write(3, 0, 'Desde:', formats['bold'])
        sheet.write(3, 1, wizard.date_from.strftime("%Y-%m-%d"), )
        sheet.write(3, 2, 'Hasta:', formats['bold'])
        sheet.write(3, 3, wizard.date_to.strftime("%Y-%m-%d"), )
        # sheet.write(4, 0, 'Sucursal:', formats['bold'])
        # sheet.write(4, 1, ', '.join([branch.name for branch in wizard.company_branch_address_ids]) if wizard.company_branch_address_ids else 'Todos', )

        sheet.write(7, 0, 'ITEM', formats['header'])
        sheet.write(7, 1, 'NOMBRE', formats['header'])
        sheet.write(7, 2, 'UNI', formats['header'])
        sheet.write(7, 3, 'CANT.', formats['header'])
        sheet.write(7, 4, 'PRECIO U.', formats['header'])
        sheet.write(7, 5, 'SUB TOTAL.', formats['header'])
        sheet.write(7, 6, 'TIPO', formats['header'])
        sheet.write(7, 7, '#DOC.', formats['header'])
        sheet.write(7, 8, 'FECHA EMI.', formats['header'])

        row = 8
        if len(_data) > 0:
            item = 1
            for rec in _data:
                sheet.write(row, 0, item, formats['normal_center'])
                sheet.write(row, 1, rec['ail_name'], formats['normal_left'])
                sheet.write(row, 2, rec['uom'].get(lang_code,'') , formats['normal_center'])
                sheet.write(row, 3, rec['quantity'], formats['format_qty'])
                sheet.write(row, 4, rec['price_unit'], formats['format_number'])
                sheet.write(row, 5, self.calculate_sub_total(rec['quantity'],rec['price_unit']) , formats['format_number'])
                if (not rec['code_journal']) or rec['code_journal'] == '00' or rec['code_journal'] == '0000':
                    sheet.write(row, 6, "TICKET", formats['normal_center'])
                elif rec['code_journal'] == '01':
                    sheet.write(row, 6, "FACTURA", formats['normal_center'])
                elif rec['code_journal'] == '03':
                    sheet.write(row, 6, "BOLETA", formats['normal_center'])
                sheet.write(row, 7, rec['ai_number'], formats['normal_center'])
                sheet.write(row, 8, rec['invoice_date'].strftime("%Y-%m-%d") if rec['invoice_date'] else "FECHA NO ESTABLECIDA", formats['normal_center'])
                row += 1
                item += 1
        else:
            sheet.write(row, 0, 'NO HAY DATOS / REPORTE EN CONSTRUCCION', formats['normal_left'])


    def calculate_sub_total(self, quantity, price_unit):
        return quantity * price_unit