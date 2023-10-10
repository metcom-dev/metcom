from odoo import fields, models, _
from markupsafe import Markup
from odoo.tools import config



class ReportAccountFinancialReportInherit(models.Model):
    _inherit = "account.report"

    allow_txt_generation = fields.Selection(selection_add=[('01', '3.1 Estado de situación financiera')])


    def _get_options(self, previous_options=None):
        # OVERRIDE
        options = super(ReportAccountFinancialReportInherit, self)._get_options(previous_options)

        # If manual values were stored in the context, we store them as options.
        # This is useful for report printing, were relying only on the context is
        # not enough, because of the use of a route to download the report (causing
        # a context loss, but keeping the options).
        if self.allow_txt_generation == '01':
            options['change_header'] = True

        return options
    
    def _init_options_buttons(self, options, previous_options=None):
        if self.allow_txt_generation == '01':
            options['buttons'] = [
                {'name': _('PDF'), 'sequence': 10, 'action': 'export_file',
                 'action_param': 'export_to_pdf', 'file_export_type': _('PDF')},
                {'name': _('XLSX'), 'sequence': 20, 'action': 'export_file',
                 'action_param': 'export_to_xlsx', 'file_export_type': _('XLSX')},
                {'name': _('Save'), 'sequence': 100,
                 'action': 'open_report_export_wizard'},
                {'name': _('Exportar a txt 3.1'), 'sequence': 121,
                 'action': 'open_report_export_txt_wizard_0301_ee'}
            ]
        else:
            options['buttons'] = [
                {'name': _('PDF'), 'sequence': 10, 'action': 'export_file',
                 'action_param': 'export_to_pdf', 'file_export_type': _('PDF')},
                {'name': _('XLSX'), 'sequence': 20, 'action': 'export_file',
                 'action_param': 'export_to_xlsx', 'file_export_type': _('XLSX')},
                {'name': _('Save'), 'sequence': 100,
                 'action': 'open_report_export_wizard'},
            ]
               
    def open_report_export_txt_wizard_0301_ee(self, options):
        self.ensure_one()
        new_context = {
            **self.env.context,
            'account_report_generation_options': options,
            'default_report_id': self.id,
        }        
        view_id = self.env.ref(
            'ple_inv_and_bal_0301_ee.wizard_report_generate_0301_ee_txt_view').id        
        new_wizard = self.with_context(new_context).env['wizard.report.generate.0301.ee'].create({
            'report_model': self._name,            
            'report_id': self.id,
        }) 
        return {
            'type': 'ir.actions.act_window',
            'name': _('Export'),
            'view_mode': 'form',
            'res_model': 'wizard.report.generate.0301.ee',
            'res_id': new_wizard.id,
            'target': 'new',
            'views': [[view_id, 'form']],
            'context': new_context,
        }         

    def get_pdf(self, options):
        # As the assets are generated during the same transaction as the rendering of the
        # templates calling them, there is a scenario where the assets are unreachable: when
        # you make a request to read the assets while the transaction creating them is not done.
        # Indeed, when you make an asset request, the controller has to read the `ir.attachment`
        # table.
        # This scenario happens when you want to print a PDF report for the first time, as the
        # assets are not in cache and must be generated. To workaround this issue, we manually
        # commit the writes in the `ir.attachment` table. It is done thanks to a key in the context.
        if self.allow_txt_generation != '01':
            return super(ReportAccountFinancialReportInherit, self).get_pdf(options)

        if not config['test_enable']:
            self = self.with_context(commit_assetsbundle=True)

        base_url = self.env['ir.config_parameter'].sudo().get_param('report.url') or self.env[
            'ir.config_parameter'].sudo().get_param('web.base.url')
        rcontext = {
            'mode': 'print',
            'base_url': base_url,
            'company': self.env.company,
        }

        body_html = self.with_context(print_mode=True).get_html(options)
        body = self.env['ir.ui.view']._render_template(
            "account_reports.print_template",
            values=dict(rcontext, body_html=body_html),
        )
        body_string = str(body)

        special_header = self.env.ref("ple_inv_and_bal_0301_ee.action_print_report_pdf", False)._render_qweb_html(self.id)[0]
        body_string = body_string.replace('<body class="o_account_reports_body_print">',
                                            '<body class="o_account_reports_body_print">' + special_header.decode())

        body = Markup(body_string)
        footer = self.env['ir.actions.report']._render_template("web.internal_layout", values=rcontext)
        footer = self.env['ir.actions.report']._render_template("web.minimal_layout", values=dict(rcontext, subst=True,
                                                                                                  body=Markup(
                                                                                                      footer.decode())))

        landscape = False
        if len(self.with_context(print_mode=True).get_header(options)[-1]) > 5:
            landscape = True
        
        return self.env['ir.actions.report']._run_wkhtmltopdf(
            [body],
            footer=footer.decode(),
            landscape=landscape,
            specific_paperformat_args={
                'data-report-margin-top': 10,
                'data-report-header-spacing': 10
            }
        )


class AccountFinancialHtmlReportLine(models.Model):
    _inherit = "account.report.line"
    
    eeff_ple_ids = fields.Many2one('eeff.ple',
        string='3.1 Rubro ESF'
    )