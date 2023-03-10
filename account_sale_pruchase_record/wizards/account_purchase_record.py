# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime, timedelta
import time
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError

import logging
log = logging.getLogger(__name__)

class PurchasesRecord(models.TransientModel):
    _name = 'report.account_purchase_record'

    company_id = fields.Many2one('res.company', string='Empresa', default=lambda self: self.env.user.company_id)
    date_from = fields.Date(string='Desde', default=fields.Date.today())
    date_to = fields.Date(string='Hasta', default=fields.Date.today())

    def init(self):
        self.env.cr.execute("""
            CREATE or REPLACE FUNCTION dte_get_tax_purchase(account_move_id INTEGER, move_type VARCHAR, l10n_document_type_code VARCHAR) 
            RETURNS RECORD
            language plpgsql
            as
            $$
            DECLARE
                TAX_TOTAL NUMERIC := 0.0;
                dte_amount_igv NUMERIC := 0.0;
                dte_amount_isc NUMERIC := 0.0;
                dte_amount_icbper NUMERIC := 0.0;
                dte_amount_others NUMERIC := 0.0;
                
                tax_name VARCHAR := '';
                tax_amount NUMERIC;
                aml_line RECORD;
                values RECORD;
            BEGIN
            FOR aml_line IN ( SELECT tgroup.name group_name, tax.tax_group_id, line.* FROM account_move_line line INNER JOIN account_tax tax ON line.tax_line_id = tax.id INNER JOIN account_tax_group tgroup ON tgroup.id = tax.tax_group_id WHERE move_id = account_move_id )
            LOOP
                tax_name = aml_line.group_name;
                tax_amount = 0.0;
                IF aml_line.debit > aml_line.credit THEN
                    tax_amount = aml_line.debit;
                ELSE
                    tax_amount = aml_line.credit;
                END IF;

                IF tax_name = 'IGV' THEN
                    dte_amount_igv := dte_amount_igv + tax_amount;
                ELSIF tax_name = 'ISC' THEN
                    dte_amount_isc := dte_amount_isc + tax_amount;
                ELSIF tax_name = 'ICBPER' THEN
                    dte_amount_icbper := dte_amount_icbper + tax_amount;
                ELSIF tax_name = 'OTROS' THEN
                    dte_amount_others := dte_amount_others + tax_amount;
                ELSE
                    tax_amount = 0.0;  
                END IF;
                TAX_TOTAL := TAX_TOTAL + tax_amount;
            END LOOP;
            IF move_type = 'in_refund' OR l10n_document_type_code = '07' THEN
                TAX_TOTAL := -1 * TAX_TOTAL;
                dte_amount_igv := -1 * dte_amount_igv;
                dte_amount_icbper := -1 * dte_amount_icbper;
                dte_amount_others := -1 * dte_amount_others;
            END IF;
            values := (ROUND(TAX_TOTAL, 2), ROUND(dte_amount_igv, 2), ROUND(dte_amount_isc, 2), ROUND(dte_amount_icbper, 2), ROUND(dte_amount_others, 2));
            RETURN values;
            END;
            $$;
        """)

    def get_data_details(self):
        sql_ext = ""
        if False:
            sql_ext = ""
        else:
            sql_ext = "LEFT JOIN l10n_latam_document_type AS ajd ON ajd.id = am.l10n_latam_document_type_id AND ajd.code IN ('01', '02', '03', '07', '08')"
        
        sql = """
            SELECT am.id account_id, am.invoice_date date_invoice, 
                am.invoice_date_due date_due, 
                COALESCE(ajd.code, '-') invoice_type_code, 
                am.name number, 
                am.ref reference,
                COALESCE(lidt.l10n_pe_vat_code, '0') doc_type, 
                rp.vat, 
                rp.name, 
                am.reversed_entry_id,
                dte_get_tax_purchase(am.id, am.move_type, ajd.code) as tax_data,
                am.amount_untaxed amount_untaxed, 
                am.amount_tax,
                am.amount_total,
            --    am.l10n_pe_dte_amount_exonerated amount_total_exonerated,
            --    am.l10n_pe_dte_amount_exportation amount_total_exportation,
                am.currency_id, 
                rc.name AS rc_name, 
                am.invoice_origin 
            FROM account_move AS am
            {sql_ext}
            INNER JOIN res_partner AS rp ON rp.id = am.partner_id 
            LEFT JOIN l10n_latam_identification_type lidt ON lidt.id = rp.l10n_latam_identification_type_id
            --LEFT JOIN res_company_branch_address AS rcb ON am.company_branch_address_id=rcb.id 
            INNER JOIN res_currency AS rc ON rc.id = am.currency_id
            WHERE am.move_type in ('in_invoice', 'in_refund')
            AND am.state in ('posted')
            AND am.company_id = {company_id}
            AND am.date >= '{date_from}'
            AND am.date <= '{date_to}'
            ORDER BY am.create_date ASC""".format(
                company_id=self.company_id.id,
                date_from=self.date_from,
                date_to=self.date_to,
                sql_ext=sql_ext,
            )

        self.env.cr.execute(sql)
        res = self.env.cr.dictfetchall()
        return res

    def export_xls(self):
        return {
            'type': 'ir.actions.report',
            'report_name': 'account_sale_purchase_record.acc_purchase_record.xlsx',
            'report_type': 'xlsx',
            'lines': self,
        }
