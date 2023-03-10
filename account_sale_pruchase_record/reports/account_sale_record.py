# -*- coding: utf-8 -*-
from odoo import models, api, fields, _
from datetime import datetime

import ast

import logging
log = logging.getLogger(__name__)


class AccountSalesRecordReportXlsx(models.AbstractModel):
    _name = 'report.account_sale_purchase_record.acc_sale_record.xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, lines):
        wizard = lines[0]
        _data = wizard.get_data_details()

        sheet = workbook.add_worksheet('VENTAS')
        sheet.set_column('A:AK', 14)
        sheet.set_column('I:I', 45)
        sheet.set_row(3, 16)
        sheet.set_row(3, 16)
        sheet.set_row(4, 75)
        formats = {
            'bold_center': workbook.add_format({'bold': True, 'align': 'center', 'valign': 'vcenter', 'text_wrap': True}),
            'bold_right': workbook.add_format({'bold': True, 'align': 'right'}),
            'normal_center': workbook.add_format({'align': 'center'}),
        }

        sheet.merge_range('A1:D1', u''+wizard.company_id.name + ' - ' + str(datetime.now().year) + ' - ' + str(datetime.now().month), formats['bold_center'])
        for i in range(1, 38):
            sheet.write(1, i-1, i, formats['bold_center'])
        row_header = 4
        sheet.merge_range(
            'A3:A5', 'NUMERO CORRELATIVO DEL REGISTRO O CODIGO UNICO DE LA OPERACION', formats['bold_center'])
        sheet.merge_range(
            'B3:B5', 'FECHA DE EMISION DEL COMPROBANTE DE PAGO O DOCUMENTO', formats['bold_center'])
        sheet.merge_range(
            'C3:C5', 'FECHA DE VENCIMIENTO Y/O PAGO', formats['bold_center'])

        sheet.merge_range(
            'D3:F4', 'COMPROBANTE DE PAGO O DOCUMENTO', formats['bold_center'])
        sheet.write(row_header, 3, 'TIPO (TABLA 10)', formats['bold_center'])
        sheet.write(
            row_header, 4, 'N DE SERIE O N DE SERIE DE LA MAQUINA REGISTRADORA', formats['bold_center'])
        sheet.write(row_header, 5, 'NUMERO', formats['bold_center'])

        sheet.merge_range('G3:I3', 'INFORMACION DEL CLIENTE',
                        formats['bold_center'])
        sheet.merge_range('G4:H4', 'DOCUMENTO DE IDENTIDAD',
                        formats['bold_center'])
        sheet.merge_range(
            'I4:I5', 'APELLIDOS Y NOMBRES, DENOMINACION O RAZON SOCIAL', formats['bold_center'])
        sheet.write(row_header, 6, 'TIPO (TABLA 2)', formats['bold_center'])
        sheet.write(row_header, 7, 'NUMERO', formats['bold_center'])

        sheet.merge_range(
            'J3:J5', 'VALOR FACTURADO DE LA EXPORTACION', formats['bold_center'])
        sheet.merge_range(
            'K3:K5', 'BASE IMPONIBLE DE LA OPERACION GRAVADA', formats['bold_center'])
        sheet.merge_range(
            'L3:M4', 'IMPORTE TOTAL DE LA OPERACION EXONERADA O INAFECTA', formats['bold_center'])
        sheet.write(row_header, 11, 'EXONERADA', formats['bold_center'])
        sheet.write(row_header, 12, 'INAFECTA', formats['bold_center'])

        sheet.merge_range('N3:N5', 'ISC', formats['bold_center'])
        sheet.merge_range('O3:O5', 'IGV Y/O IPM', formats['bold_center'])
        sheet.merge_range('P3:P5', 'ICBPER', formats['bold_center'])
        sheet.merge_range(
            'Q3:Q5', 'IMPORTE TOTAL DEL COMPROBANTE DE PAGO', formats['bold_center'])
        sheet.merge_range('R3:R5', 'TIPO DE CAMBIO', formats['bold_center'])

        sheet.merge_range(
            'S3:V4', 'REFERENCIA DEL COMPROBANTE DE PAGO O DOCUMENTO ORIGINAL QUE SE MODIFICA', formats['bold_center'])
        sheet.write(row_header, 18, 'FECHA', formats['bold_center'])
        sheet.write(row_header, 19, 'TIPO (TABLA 10)', formats['bold_center'])
        sheet.write(row_header, 20, 'SERIE', formats['bold_center'])
        sheet.write(
            row_header, 21, 'N DEL COMPROBANTE DE PAGO O DOCUMENTO', formats['bold_center'])
        sheet.write(row_header, 22, 'MONEDA', formats['bold_center'])
        sheet.write(row_header, 23, 'ESTADO', formats['bold_center'])
        sheet.write(row_header, 24, 'OBSERVACIONES', formats['bold_center'])
        sheet.write(row_header, 25, 'CAMPO 1', formats['bold_center'])
        sheet.write(row_header, 26, 'CAMPO 2', formats['bold_center'])
        sheet.write(row_header, 27, 'CAMPO 3', formats['bold_center'])
        sheet.write(row_header, 28, 'CAMPO 4', formats['bold_center'])
        sheet.write(row_header, 29, 'CAMPO 5', formats['bold_center'])
        sheet.write(row_header, 30, 'CAMPO 6', formats['bold_center'])
        sheet.write(row_header, 31, 'CAMPO 7', formats['bold_center'])
        sheet.write(row_header, 32, 'CAMPO 8', formats['bold_center'])

        row = 5
        index = 1
        estados = {
            'draft': 'SIN EMITIR',
            'posted': 'EMITIDO',
            'cancel': 'ANULADO',
        }
        if len(_data) > 0:
            for rec in _data:
                
                extra_values = self._get_extra_values(rec['account_id'])
                
                currency_rate = 1
                if rec['rc_name'] == 'USD':
                    if abs(rec['am_amount_untaxed_signed']) and abs(rec['am_amount_untaxed'])>0:
                        currency_rate = round(abs(rec['am_amount_untaxed_signed'])/abs(rec['am_amount_untaxed']),3)

                    rec['amount_total_exportation'] = round(extra_values['amount_total_exportation']*currency_rate,2)
                    rec['amount_untaxed'] = round(rec['amount_untaxed']*currency_rate,2)
                    rec['amount_total_exonerated'] = round(extra_values['amount_total_exonerated']*currency_rate,2)
                    rec['amount_total_unaffected'] = round(extra_values['amount_total_unaffected']*currency_rate,2)
                    rec['amount_total'] = round(rec['amount_total']*currency_rate,2)
                    '''currency_rate = self.env['res.currency.rate'].search(
                        [('currency_id', '=', rec['currency_id']), ('name', 'like', rec['date_invoice'])]).read(['rate'])
                    if len(currency_rate) > 0:
                        sheet.write(row, 22 + 1, currency_rate[0]['rate'], )
                    else:
                        temp_date = datetime.strptime(
                            rec['date_invoice'], '%Y-%m-%d')
                        if datetime.weekday(temp_date) == 2:
                            temp_date += timedelta(days=1)
                            currency_rate = self.env['res.currency.rate'].search(
                                [('currency_id', '=', rec['currency_id']), ('name', 'like', rec['date_invoice'])]).read(['rate'])
                            sheet.write(
                                row, 22 + 1, currency_rate[0]['rate'], )'''
                rec['date_invoice'] = datetime.strftime(rec['date_invoice'], '%d/%m/%Y')
                if rec.get('date_due', False) or rec.get('date_due') != None:
                    rec['date_due'] = datetime.strftime(rec['date_due'], '%d/%m/%Y')
                sheet.write(row, 0, index, formats['normal_center'])
                sheet.write(row, 0 + 1, rec['date_invoice'], formats['normal_center'])
                sheet.write(row, 1 + 1, rec['date_due'], formats['normal_center'])
                sheet.write(row, 2 + 1, rec['invoice_type_code'], formats['normal_center'])
                if rec['invoice_series'][-1:] == '-':
                    sheet.write(row, 3 + 1, rec['invoice_series'][:-1], formats['normal_center'])
                else:
                    sheet.write(row, 3 + 1, rec['invoice_series'], formats['normal_center'])

                sheet.write(row, 4 + 1, rec['invoice_secuence'], formats['normal_center'])
                sheet.write(row, 5 + 1, rec['doc_type'] if rec['doc_type'] != None else 'No Ingresado', formats['normal_center'])
                sheet.write(row, 6 + 1, rec['vat'], formats['normal_center'])
                sheet.write(row, 7 + 1, rec['name'], )

                tax_data = ast.literal_eval(rec['tax_data'])
                sheet.write(row, 8 + 1, extra_values['amount_total_exportation'] if rec['invoice_type_code'] != '07' else extra_values['amount_total_exportation'] * -1, )
                # sheet.write(row, 8 + 1, "not field" )

                sheet.write(row, 9 + 1, rec['amount_untaxed'] if rec['invoice_type_code'] != '07' else rec['amount_untaxed'] * -1, )
                # sheet.write(row, 9 + 1, "not field" )

                sheet.write(row, 10 + 1, extra_values['amount_total_exonerated'] if rec['invoice_type_code'] != '07' else extra_values['amount_total_exonerated'] * -1, )
                # sheet.write(row, 10 + 1, "not field" )

                sheet.write(row, 11 + 1, extra_values['amount_total_unaffected'] if rec['invoice_type_code'] != '07' else extra_values['amount_total_unaffected'] * -1, )
                # sheet.write(row, 11 + 1, "not field" )
                
                sheet.write(row, 12 + 1, round(tax_data[2]*currency_rate,2), )
                sheet.write(row, 13 + 1, round(tax_data[1]*currency_rate,2), )
                sheet.write(row, 14 + 1, round(tax_data[3]*currency_rate,2), )
                sheet.write(row, 15 + 1, rec['amount_total'] if rec['invoice_type_code'] != '07' else rec['amount_total'] * -1, )
                sheet.write(row, 16 + 1, currency_rate, )

                if estados.get(rec['state']) == 'ANULADO':
                    sheet.write(row, 9 + 1, 0, )
                    sheet.write(row, 10 + 1, 0, )
                    sheet.write(row, 11 + 1, 0, )
                    sheet.write(row, 12 + 1, 0, )
                    sheet.write(row, 13 + 1, 0, )
                    sheet.write(row, 14 + 1, 0, )
                    sheet.write(row, 15 + 1, 0, )

                if rec['invoice_type_code'] == '07':
                    invoice_origin = self.env['account.move'].browse(rec['reversed_entry_id'])
                    if len(invoice_origin) == 1:
                        invoice_type_code = '-'

                        invoice_type_code = invoice_origin.l10n_latam_document_type_id.code

                        sheet.write(row, 17 + 1, datetime.strftime(invoice_origin.invoice_date, '%d/%m/%Y'), formats['normal_center'])
                        sheet.write(row, 18 + 1, invoice_type_code, formats['normal_center'])
                        '''if invoice_origin.prefix_val and invoice_origin.suffix_val:
                            sheet.write(row, 19 + 1, invoice_origin.prefix_val, formats['normal_center'])
                            sheet.write(row, 20 + 1, invoice_origin.suffix_val, formats['normal_center'])'''

                if estados.get(rec['state']) == 'ANULADO':
                    sheet.write(row, 17 + 1, 0, formats['normal_center'])
                    sheet.write(row, 18 + 1, 0, formats['normal_center'])
                    sheet.write(row, 19 + 1, 0, formats['normal_center'])
                    sheet.write(row, 20 + 1, 0, formats['normal_center'])

                sheet.write(row, 22, rec['rc_name'], formats['normal_center'])
                sheet.write(row, 23, estados.get(rec['state']), formats['normal_center'])

                if rec['am_narration'] == None or rec['am_narration'] == '<p><br></p>':
                    sheet.write(row, 24, '-', formats['normal_center'])
                else:
                    sheet.write(row, 24, rec['am_narration'], formats['normal_center'])
                row += 1
                index += 1
            sheet.write(row+2, 8, 'TOTAL', formats['bold_right'])
            sheet.write(row+2, 9, '=SUM(J4:J'+str(row)+')', formats['bold_right'])
            sheet.write(row+2, 10, '=SUM(K4:K'+str(row)+')', formats['bold_right'])
            sheet.write(row+2, 11, '=SUM(L4:L'+str(row)+')', formats['bold_right'])
            sheet.write(row+2, 12, '=SUM(M4:M'+str(row)+')', formats['bold_right'])
            sheet.write(row+2, 13, '=SUM(N4:N'+str(row)+')', formats['bold_right'])
            sheet.write(row+2, 14, '=SUM(O4:O'+str(row)+')', formats['bold_right'])
            sheet.write(row+2, 15, '=SUM(P4:P'+str(row)+')', formats['bold_right'])
            sheet.write(row+2, 16, '=SUM(Q4:Q'+str(row)+')', formats['bold_right'])
        else:
            sheet.write(row, 0, 'NO HAY DATOS / REPORTE EN CONSTRUCCION', )

    @api.model
    def _get_extra_values(self, move_id):
        invoice = self.env['account.move'].sudo().browse(move_id)
        #get lines from invoice
        lines = invoice.invoice_line_ids
        # obtener los impuestos de las lineas
        taxes = lines.mapped('tax_ids')

        # obtener los impuestos de las lineas que sean EXP
        export_taxes = taxes.filtered(lambda x: x.l10n_pe_edi_tax_code == '9995')
        # obtener los impuestos de las lineas que sean EXO
        exempt_taxes = taxes.filtered(lambda x: x.l10n_pe_edi_tax_code == '9997')
        # obtener los impuestos de las lineas que sean INA
        unaffiliated_taxes = taxes.filtered(lambda x: x.l10n_pe_edi_tax_code == '9998')

        export_tax_amount = 0
        exempt_tax_amount = 0
        unaffiliated_tax_amount = 0

        if export_taxes:
            if sum(taxes.mapped('amount')) != 0:
                export_tax_amount = sum(export_taxes.mapped('amount')) / sum(taxes.mapped('amount')) * sum(lines.mapped('price_subtotal'))

        if exempt_taxes:
            if sum(taxes.mapped('amount')) != 0:
                exempt_tax_amount = sum(exempt_taxes.mapped('amount')) / sum(taxes.mapped('amount')) * sum(lines.mapped('price_subtotal'))

        if unaffiliated_taxes:
            if sum(taxes.mapped('amount')) != 0:
                unaffiliated_tax_amount = sum(unaffiliated_taxes.mapped('amount')) / sum(taxes.mapped('amount')) * sum(lines.mapped('price_subtotal'))

        return {
            'amount_total_exportation': export_tax_amount,
            'amount_total_exonerated': exempt_tax_amount,
            'amount_total_unaffected': unaffiliated_tax_amount,
        }
    
    

