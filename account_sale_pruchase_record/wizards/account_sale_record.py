# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime, timedelta
import time
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError

import logging
log = logging.getLogger(__name__)

class SalesRecord(models.TransientModel):
    _name = 'report.account_sale_record'

    company_id = fields.Many2one('res.company', string='Empresa', default=lambda self: self.env.user.company_id)
    # company_branch_address_ids = fields.Many2many(string='Sucursales', comodel_name='res.company.branch.address')
    date_from = fields.Date(string='Desde', default=fields.Date.today())
    date_to = fields.Date(string='Hasta', default=fields.Date.today())

    def init(self):
        self.env.cr.execute("""
            CREATE or REPLACE FUNCTION dte_get_tax(account_move_id INTEGER, move_type VARCHAR, l10n_document_type_code VARCHAR) 
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
                dte_amount_perception NUMERIC := 0.0;
                dte_amount_perception_base NUMERIC := 0.0;
                
                tax_name VARCHAR := '';
                tax_amount NUMERIC;
                aml_line RECORD;
                values RECORD;
            BEGIN
            FOR aml_line IN ( SELECT tgroup.name group_name, tax.tax_group_id, line.* FROM account_move_line line INNER JOIN account_tax tax ON line.tax_line_id = tax.id INNER JOIN account_tax_group tgroup ON tgroup.id = tax.tax_group_id WHERE move_id = account_move_id )
            LOOP
                tax_name = aml_line.group_name;
                tax_amount = 0.0;
                IF move_type = 'out_refund' AND l10n_document_type_code = '07' THEN
                    tax_amount = ABS(aml_line.balance) * -1;
                ELSE
                    tax_amount = aml_line.balance * -1;
                END IF;
                IF tax_name = 'IGV' THEN
                    dte_amount_igv := dte_amount_igv + tax_amount;
                ELSIF tax_name = 'ISC' THEN
                    dte_amount_isc := dte_amount_isc + tax_amount;
                ELSIF tax_name = 'ICBPER' THEN
                    dte_amount_icbper := dte_amount_icbper + tax_amount;
                ELSIF tax_name = 'OTROS' THEN
                    dte_amount_others := dte_amount_others + tax_amount;
                ELSIF tax_name = 'PER' THEN
                    dte_amount_perception := dte_amount_perception + tax_amount;
                    dte_amount_perception_base := dte_amount_perception_base + aml_line.tax_base_amount;
                ELSE
                    tax_amount = 0.0;  
                END IF;
                TAX_TOTAL := TAX_TOTAL + tax_amount;
            END LOOP;
            values := (ROUND(TAX_TOTAL, 2), ROUND(dte_amount_igv, 2), ROUND(dte_amount_isc, 2), ROUND(dte_amount_icbper, 2), ROUND(dte_amount_others, 2), ROUND(dte_amount_perception, 2), ROUND(dte_amount_perception_base, 2));
            RETURN values;
            END;
            $$;
        """)

    def get_data_details(self):
        sql_ext = ""
        invoice_serial = "substr(am.name, 1, 4)"
        invoice_number = "substr(am.name, 6)"
        if False:
            sql_ext = ""
        else:
            sql_ext = "INNER JOIN l10n_latam_document_type AS ajd ON ajd.id = am.l10n_latam_document_type_id AND ajd.code IN ('01', '03', '07', '08')"
            invoice_serial = "substr(am.name, 5, 4)"
            invoice_number = "substr(am.name, 10)"

        sql = """
            SELECT am.id account_id, am.state,
                am.reversed_entry_id, 
                am.invoice_date date_invoice, 
                am.invoice_date_due date_due, 
                ajd.code invoice_type_code, 
                {invoice_serial} AS invoice_series,
                {invoice_number} AS invoice_secuence, 
                COALESCE(lidt.l10n_pe_vat_code, '0') doc_type, 
                rp.vat, 
                rp.name,
                dte_get_tax(am.id, am.move_type, ajd.code) as tax_data,
                am.amount_total,
                am.amount_untaxed amount_untaxed,
            --    am.l10n_pe_dte_amount_unaffected amount_total_unaffected, 
            --    am.l10n_pe_dte_amount_exonerated amount_total_exonerated,
            --    am.l10n_pe_dte_amount_exportation amount_total_exportation,
                am.currency_id, 
                rc.name AS rc_name, 
                am.invoice_origin origin,
                am.narration am_narration
            FROM account_move AS am
            {sql_ext}
            INNER JOIN res_partner AS rp ON rp.id = am.partner_id
            LEFT JOIN l10n_latam_identification_type lidt ON lidt.id = rp.l10n_latam_identification_type_id
            INNER JOIN res_currency AS rc ON rc.id = am.currency_id
            WHERE am.move_type in ('out_invoice', 'out_refund')
            AND am.state in ('posted','cancel')
            AND am.invoice_date >= '{date_from}'
            AND am.invoice_date <= '{date_to}'
            ORDER BY am.invoice_date ASC
            """.format(
                sql_ext=sql_ext,
                company_id=self.company_id.id,
                date_from=self.date_from,
                date_to=self.date_to,
                invoice_serial=invoice_serial,
                invoice_number=invoice_number
            )

        self.env.cr.execute(sql)
        res = self.env.cr.dictfetchall()
        return res

    def export_xls(self):
        return {
            'type': 'ir.actions.report',
            'report_name': 'account_sale_purchase_record.acc_sale_record.xlsx',
            'report_type': 'xlsx',
            'lines': self,
        }
