# -*- coding: utf-8 -*-
from odoo import models, api, fields, _
from datetime import datetime

import ast

import logging
log = logging.getLogger(__name__)


class AccountPurchasesRecordReportXlsx(models.AbstractModel):
    _name = 'report.account_sale_purchase_record.acc_purchase_record.xlsx'
    _inherit = 'report.report_xlsx.abstract'
    _description = 'Excel de Reporte Registro de Compras'

    def generate_xlsx_report(self, workbook, data, lines):
        wizard = lines[0]
        _data = wizard.get_data_details()

        sheet = workbook.add_worksheet('COMPRAS')
        sheet.set_column('A:AK', 14)
        sheet.set_column('J:J', 50)
        sheet.set_column('G:G', 38)
        sheet.set_row(2, 32)
        sheet.set_row(3, 25)
        sheet.set_row(4, 80)
        formats = {
            'bold_center': workbook.add_format({'bold': True, 'align': 'center', 'valign': 'vcenter', 'text_wrap': True}),
            'bold_right': workbook.add_format({'bold': True, 'align': 'right'}),
            'normal_center': workbook.add_format({'align': 'center'}),
        }
        
        sheet.merge_range('A1:D1', u''+wizard.company_id.name + ' - ' + str(datetime.now().year) + ' - ' + str(datetime.now().month), formats['bold_center'])
        for i in range(1, 40):
            sheet.write(1, i-1, i, formats['bold_center'])
        row_header= 4
        sheet.merge_range('A3:A5', 'NUMERO CORRELATIVO DEL REGISTRO O CODIGO UNICO DE LA OPERACION', formats['bold_center'])
        sheet.merge_range('B3:B5', 'FECHA DE EMISION DEL COMPROBANTE DE PAGO O DOCUMENTO', formats['bold_center'])
        sheet.merge_range('C3:C5', 'FECHA DE VENCIMIENTO O FECHA DE PAGO', formats['bold_center'])
        
        sheet.merge_range('D3:F4', 'COMPROBANTE DE PAGO O DOCUMENTO', formats['bold_center'])
        sheet.write(row_header, 3, 'TIPO (TABLA 10)', formats['bold_center'])
        sheet.write(row_header, 4, 'SERIE O CODIGO DE LA DEPENDENCIA ADUANERA (TABLA 11)', formats['bold_center'])
        sheet.write(row_header, 5, u'AÑO DE EMISION DE LA DUA O DSI', formats['bold_center'])

        sheet.merge_range('G3:G5', 'N° DEL COMPROBANTE DE PAGO, DOCUMENTO, N° DE ORDEN DEL FORMULARIO FÍSICO O VIRTUAL, N° DE DUA, DSI O LIQUIDACION DE COBRANZA U OTROS DOCUMENTOS EMITIDOS POR SUNAT PARA ACREDITAR EL CRÉDITO FISCAL EN LA IMPORTACION', formats['bold_center'])

        sheet.merge_range('H3:J3', 'INFORMACION DEL PROVEEDOR', formats['bold_center'])
        sheet.merge_range('H4:I4', 'DOCUMENTO DE IDENTIDAD', formats['bold_center'])
        sheet.merge_range('J4:J5', 'APELLIDOS Y NOMBRES, DENOMINACION O RAZON SOCIAL', formats['bold_center'])
        sheet.write(row_header, 7, 'TIPO (TABLA 2)', formats['bold_center'])
        sheet.write(row_header, 8, 'NUMERO', formats['bold_center'])
        
        sheet.merge_range('K3:L4', 'ADQUISICIONES GRAVADAS DESTINADAS A OPERACIONES GRAVADAS Y/O DE EXPORTACION', formats['bold_center'])
        sheet.write(row_header, 10, 'BASE IMPONIBLE', formats['bold_center'])
        sheet.write(row_header, 11, 'IGV', formats['bold_center'])

        sheet.merge_range('M3:N4', 'BASE IMPONIBLE GRAVADAS DESTINADAS A OPERACIONES GRAVADAS Y/O DE EXPORTACION Y A OPERACIONES NO GRAVADAS', formats['bold_center'])
        sheet.write(row_header, 12, 'BASE IMPONIBLE', formats['bold_center'])
        sheet.write(row_header, 13, 'IGV', formats['bold_center'])

        sheet.merge_range('O3:P4', 'ADQUISICIONES GRAVADAS DESTINADAS A OPERACIONES NO GRAVADAS', formats['bold_center'])
        sheet.write(row_header, 14, 'BASE IMPONIBLE', formats['bold_center'])
        sheet.write(row_header, 15, 'IGV', formats['bold_center'])

        sheet.merge_range('Q3:Q5', 'VALOR DE LAS ADQUISICIONES NO GRAVADAS', formats['bold_center'])
        sheet.merge_range('R3:R5', 'ISC', formats['bold_center'])
        sheet.merge_range('S3:S5', 'OTROS TRIBUTOS Y CARGOS', formats['bold_center'])

        sheet.merge_range('T3:T5', 'IMPORTE TOTAL', formats['bold_center'])
        sheet.merge_range('U3:U5', 'N° DE COMPROBANTE DE PAGO EMITIDO POR SUJETO NO DOMICILIADO (2)', formats['bold_center'])

        sheet.merge_range('V3:W4', 'CONSTANCIA DE DEPOSITO DE DETRACCION (3)', formats['bold_center'])
        sheet.write(row_header, 21, 'NUMERO', formats['bold_center'])
        sheet.write(row_header, 22, 'FECHA DE EMISION', formats['bold_center'])

        sheet.merge_range('X3:X5', 'TIPO DE CAMBIO', formats['bold_center'])

        sheet.merge_range('Y3:AB4', 'REFERENCIA DEL COMPROBANTE DE PAGO O DOCUMENTO ORIGINAL QUE SE MODIFICA', formats['bold_center'])
        sheet.write(row_header, 24, 'FECHA', formats['bold_center'])
        sheet.write(row_header, 25, 'TIPO (TABLA 10)', formats['bold_center'])
        sheet.write(row_header, 26, 'SERIE', formats['bold_center'])
        sheet.write(row_header, 27, 'N DEL COMPROBANTE DE PAGO O DOCUMENTO', formats['bold_center'])
        sheet.merge_range('AC3:AC5', 'MONEDA', formats['bold_center'])

        row = 5
        index = 1
        if len(_data) > 0:
            total_soles = {
                'amount_total_taxable': 0,
                'amount_total_iva': 0,
                'amount_total_exonerated': 0,
                'amount_total_isc': 0,
                'amount_total_other_taxes': 0,
                'amount_total': 0,
            }
            total_dolares = {
                'amount_total_taxable': 0,
                'amount_total_iva': 0,
                'amount_total_exonerated': 0,
                'amount_total_isc': 0,
                'amount_total_other_taxes': 0,
                'amount_total': 0,
            }
            for rec in _data:
                
                extra_values = self._get_extra_values(rec['account_id'])

                tax_data = ast.literal_eval(rec['tax_data'])
                if rec['invoice_type_code'] == '07':
                    rec['amount_total_taxable'] = -1*rec['amount_untaxed']
                    extra_values['amount_total_exonerated'] = -1*extra_values['amount_total_exonerated']
                    rec['amount_total'] = -1*rec['amount_total']
                    rec['amount_untaxed'] = -1*rec['amount_untaxed']
                    rec['amount_tax'] = -1*rec['amount_tax']
                serial = ''
                number = ''
                if rec.get('number', False) and rec.get('invoice_type_code') in ('01', '03', '07', '08'):
                    number = rec.get('number').split('-')
                    if len(number) == 2:
                        serial = number[0]
                        number = number[1]
                    else:
                        number = rec.get('number')
                rec['date_invoice'] = datetime.strftime(rec['date_invoice'], '%d/%m/%Y')
                if rec.get('date_due', False) or rec.get('date_due') != None:
                    rec['date_due'] = datetime.strftime(rec['date_due'], '%d/%m/%Y')
                sheet.write(row, 0, index, formats['normal_center'])
                sheet.write(row, 1, rec['date_invoice'], formats['normal_center'])
                sheet.write(row, 2, rec['date_due'], formats['normal_center'])
                sheet.write(row, 3, rec['invoice_type_code'], formats['normal_center'])
                if rec['reference']:
                    if rec['reference'].find('-'):
                        temp_invoice_num = rec['reference'].split('-')
                        invoice_serial = ''
                        invoice_number = ''
                        if len(temp_invoice_num) == 2:
                            invoice_serial = temp_invoice_num[0]
                            invoice_number = temp_invoice_num[1]
                        sheet.write(row, 4, invoice_serial,
                                    formats['normal_center'])
                        sheet.write(row, 6, invoice_number,
                                    formats['normal_center'])
                    else:
                        sheet.write(row, 4, rec['reference'],
                                    formats['normal_center'])
                                    
                sheet.write(row, 7, rec['doc_type'] if rec['doc_type']
                            != None else 'No Ingresado', formats['normal_center'])
                sheet.write(row, 8, rec['vat'], formats['normal_center'])
                sheet.write(row, 9, rec['name'], )
                sheet.write(row, 10, rec['amount_untaxed'], )

                sheet.write(row, 11, tax_data[1], )
                sheet.write(row, 12, 0.0, )
                sheet.write(row, 13, 0.0, )
                sheet.write(row, 14, 0.0, )
                sheet.write(row, 15, 0.0, )
                sheet.write(row, 16, extra_values['amount_total_exonerated'], )

                sheet.write(row, 17, tax_data[2], )
                sheet.write(row, 18, tax_data[4])
                sheet.write(row, 19, rec['amount_total'], )

                if rec['invoice_type_code'] in ('07','08'):
                    if rec['reversed_entry_id']:
                        invoice_origin = self.env['account.move'].browse(rec['reversed_entry_id'])
                        if len(invoice_origin) == 1:
                            sheet.write(row, 24, datetime.strftime(invoice_origin.invoice_date,'%d/%m/%Y'), formats['normal_center'])
                            if invoice_origin.prefix_val and invoice_origin.suffix_val:
                                sheet.write(row, 26, invoice_origin.prefix_val, formats['normal_center'])
                                sheet.write(row, 27, invoice_origin.suffix_val, formats['normal_center'])

                if rec['rc_name'] == 'PEN':
                    total_soles['amount_total_taxable'] += rec['amount_untaxed']
                    total_soles['amount_total_iva'] += tax_data[1]
                    total_soles['amount_total_exonerated'] += extra_values['amount_total_exonerated']
                    total_soles['amount_total_isc'] += tax_data[2]
                    total_soles['amount_total_other_taxes'] += tax_data[4]
                    total_soles['amount_total'] += rec['amount_total']
                elif rec['rc_name'] == 'USD':
                    total_dolares['amount_total_taxable'] += rec['amount_untaxed']
                    total_dolares['amount_total_iva'] += tax_data[1]
                    total_dolares['amount_total_exonerated'] += extra_values['amount_total_exonerated']
                    total_dolares['amount_total_isc'] += tax_data[2]
                    total_dolares['amount_total_other_taxes'] += tax_data[4]
                    total_dolares['amount_total'] += rec['amount_total']

                sheet.write(row, 28, rec['rc_name'], formats['normal_center'])
                
                row += 1
                index += 1
            sheet.write(row+2, 9, 'TOTAL SOLES', formats['bold_right'])
            sheet.write(row+2, 10, total_soles['amount_total_taxable'], formats['bold_right'])
            sheet.write(row+2, 11, total_soles['amount_total_iva'], formats['bold_right'])
            sheet.write(row+2, 15, total_soles['amount_total_exonerated'], formats['bold_right'])
            sheet.write(row+2, 16, total_soles['amount_total_isc'], formats['bold_right'])
            sheet.write(row+2, 18, total_soles['amount_total_other_taxes'], formats['bold_right'])
            sheet.write(row+2, 19, total_soles['amount_total'], formats['bold_right'])

            sheet.write(row+3, 9, 'TOTAL DOLARES', formats['bold_right'])
            sheet.write(row+3, 10, total_dolares['amount_total_taxable'], formats['bold_right'])
            sheet.write(row+3, 11, total_dolares['amount_total_iva'], formats['bold_right'])
            sheet.write(row+3, 15, total_dolares['amount_total_exonerated'], formats['bold_right'])
            sheet.write(row+3, 16, total_dolares['amount_total_isc'], formats['bold_right'])
            sheet.write(row+3, 18, total_dolares['amount_total_other_taxes'], formats['bold_right'])
            sheet.write(row+3, 19, total_dolares['amount_total'], formats['bold_right'])
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
