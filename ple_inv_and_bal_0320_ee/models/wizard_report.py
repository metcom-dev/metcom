import base64
import time

from odoo import models, fields
from ..reports.formula import FormulaSolver
from ..reports.ple_inv_and_bal_20_report import ReportInvBal20Txt
from odoo.tools import config, date_utils

class WizardReportGenerateTxt(models.TransientModel):
    _name = 'wizard.report.generate.txt'
    _description = 'Financial report 20.0 - Wizard'

    report_model = fields.Char(string="Report Model", required=True)
    report_id = fields.Integer(string="Parent Report Id", required=True)
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Compañía',
        default=lambda self: self.env.company,
        required=True
    )
    date_start = fields.Date(
        string='Fecha Inicio',
        required=True,
        default=lambda *date_start: time.strftime('%Y-01-01')
    )
    date_end = fields.Date(
        string='Fecha Fin',
        required=True,
        default=lambda *date_end: time.strftime('%Y-12-31')
    )
    state_send = fields.Selection(selection=[
        ('0', 'Cierre de Operaciones - Bajo de Inscripciones en el RUC'),
        ('1', 'Empresa o Entidad Operativa'),
        ('2', 'Cierre de libro - No Obligado a llevarlo')
    ], required=True,
        string='Estado de Envío',
        default='0'
    )
    date_ple = fields.Date(
        string='Generado el',
        required=True,
        default=lambda date_ple: fields.Date.context_today(date_ple),
        readonly=True
    )
    financial_statements_catalog = fields.Selection(
        selection=[
            ('01', 'SUPERINTENDENCIA DEL MERCADO DE VALORES - SECTOR DIVERSAS - INDIVIDUAL'),
            ('02', 'SUPERINTENDENCIA DEL MERCADO DE VALORES - SECTOR SEGUROS - INDIVIDUAL'),
            ('03', 'SUPERINTENDENCIA DEL MERCADO DE VALORES - SECTOR BANCOS Y FINANCIERAS - INDIVIDUAL'),
            ('04', 'SUPERINTENDENCIA DEL MERCADO DE VALORES - ADMINISTRADORAS DE FONDOS DE PENSIONES (AFP)'),
            ('05', 'SUPERINTENDENCIA DEL MERCADO DE VALORES - AGENTES DE INTERMEDIACIÓN'),
            ('06', 'SUPERINTENDENCIA DEL MERCADO DE VALORES - FONDOS DE INVERSIÓN'),
            ('07', 'SUPERINTENDENCIA DEL MERCADO DE VALORES - PATRIMONIO EN FIDEICOMISOS'),
            ('08', 'SUPERINTENDENCIA DEL MERCADO DE VALORES - ICLV'),
            ('09', 'OTROS NO CONSIDERADOS EN LOS ANTERIORES')
        ],
        string='Catálogo estados financieros',
        default='09',
        required=True,
    )
    eeff_presentation_opportunity = fields.Selection(
        selection=[
            ('01', 'Al 31 de diciembre'),
            ('02', 'Al 31 de enero, por modificación del porcentaje'),
            ('03', 'Al 30 de junio, por modificación del coeficiente o porcentaje'),
            ('04',
             'Al último día del mes que sustentará la suspensión o modificación del coeficiente (distinto al 31 de enero o 30 de junio)'),
            ('05',
             'Al día anterior a la entrada en vigencia de la fusión, escisión y demás formas de reorganización de sociedades o emperesas o extinción '
             'de la persona jurídica'),
            ('06', 'A la fecha del balance de liquidación, cierre o cese definitivo del deudor tributario'),
            ('07', 'A la fecha de presentación para libre propósito')
        ],
        string='Oportunidad de presentación de EEFF',
        required=True,
        default='01'
    )
    txt_filename = fields.Char(string='Filaname .txt')
    txt_binary = fields.Binary(string='Reporte .TXT 3.20')
    
    def action_generate_txt(self):

        self.ensure_one()
        data = self.generate_data()
        report_20 = ReportInvBal20Txt(self, data)
        data = {
            'txt_binary': base64.b64encode(report_20.get_content().encode() or '\n'.encode()),
            'txt_filename': report_20.get_filename(),
        }
        self.write(data)

        return self.action_return_wizard()

    def generate_data(self):
        data = []
        report = self.env['account.report'].browse(self.report_id)        
        options = report._get_options()    
        options['date']['date_from'] = self.date_start.strftime('%Y-%m-%d')
        options['date']['date_to'] = self.date_end.strftime('%Y-%m-%d')    
        periods_options_list = self._generate_periods_options_list(options['date'])
        solver = FormulaSolver(periods_options_list, report)
        balance_rubro = 0                
        for line in report.line_ids:
            eeff = line.re_item 
            if eeff.eeff_type != '3.20':
                continue    
            solver._get_amls_results(line, '')            
            values = list(solver._get_formula_results(line).values())
            subformula = solver._get_subformula_results(line)        
            if values:               
                if(subformula=='-sum'):
                    balance_rubro = -sum(self.env['account.move.line'].search(values[0]).mapped('balance'))
                if(subformula=='sum'):
                    balance_rubro = sum(self.env['account.move.line'].search(values[0]).mapped('balance'))   
                data.append({
                    'period': self.date_end.strftime('%Y%m%d'),
                    'code': self.financial_statements_catalog,
                    'code_rubro_estado_fin': eeff.code,
                    'balance_rubro_cont': "{:.2f}".format(balance_rubro),
                    'indicador': '1',
                })               
        return data
    
    def _generate_periods_options_list(self, date_options):
        periods_options_list = []
    
        if date_options.get('mode') == 'range':
            periods_options_list.append(date_options)
        else:
            date_to = fields.Date.from_string(date_options['date_to'])
            date_from, _ = date_utils.get_month(date_to)
            date_options['date_from'] = fields.Date.to_string(date_from)
            periods_options_list.append(date_options)
    
        return periods_options_list
    
    def action_return_wizard(self):
            wizard_form_id = self.env.ref('ple_inv_and_bal_0320_ee.wizard_report_generate_txt_view').id
            return {
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'wizard.report.generate.txt',
                'views': [(wizard_form_id, 'form')],
                'view_id': wizard_form_id,
                'res_id': self.id,
                'target': 'new'
            }
