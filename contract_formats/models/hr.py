import base64
import copy
import datetime
import dateutil.relativedelta as relativedelta
import logging
import functools
from werkzeug import urls
from odoo import _, api, fields, models, tools

_logger = logging.getLogger(__name__)
try:
    # We use a jinja2 sandboxed environment to render mako templates.
    # Note that the rendering does not cover all the mako syntax, in particular
    # arbitrary Python statements are not accepted, and not all expressions are
    # allowed: only "public" attributes (not starting with '_') of objects may
    # be accessed.
    # This is done on purpose: it prevents incidental or malicious execution of
    # Python code that may break the security of the server.
    from jinja2.sandbox import SandboxedEnvironment

    mako_template_env = SandboxedEnvironment(
        block_start_string="<%",
        block_end_string="%>",
        variable_start_string="${",
        variable_end_string="}",
        comment_start_string="<%doc>",
        comment_end_string="</%doc>",
        line_statement_prefix="%",
        line_comment_prefix="##",
        trim_blocks=True,  # do not output newline after blocks
        autoescape=True,  # XML/HTML automatic escaping
    )
    mako_template_env.globals.update({
        'str': str,
        'quote': urls.url_quote,
        'urlencode': urls.url_encode,
        'datetime': datetime,
        'len': len,
        'abs': abs,
        'min': min,
        'max': max,
        'sum': sum,
        'filter': filter,
        'reduce': functools.reduce,
        'map': map,
        'round': round,

        # dateutil.relativedelta is an old-style class and cannot be directly
        # instanciated wihtin a jinja2 expression, so a lambda "proxy" is
        # is needed, apparently.
        'relativedelta': lambda *a, **kw: relativedelta.relativedelta(*a, **kw),
    })
    mako_safe_template_env = copy.copy(mako_template_env)
    mako_safe_template_env.autoescape = False
except ImportError:
    _logger.warning("jinja2 not available, templating features will not work!")


class HrContract(models.Model):
    _inherit = 'hr.contract'

    service_duration = fields.Char(
        string=u'Duración de contrato',
        compute='compute_service_duration',
        store=True
    )
    additional_info = fields.Text(
        string='Información adicional para contrato'
    )
    contract_template_id = fields.Many2one(
        comodel_name='mail.template',
        string='Usar plantilla para contrato',
        default=lambda self: self.env.ref('contract_formats.template_hr_contract', raise_if_not_found=False)
    )
    contract_name = fields.Char(
        string='Nombre de contrato - PDF'
    )
    contract_binary = fields.Binary(
        string='Contrato generado',
    )

    def get_date_start_related_contract(self):
        if self.contract_ids:
            return self.contract_ids[0].date_start if self.contract_ids[0].date_start else False
        return False

    def get_service_duration_related_contract(self):
        if self.contract_ids:
            return self.contract_ids[0].service_duration if self.contract_ids[0].service_duration else False
        return False

    def get_render_template_contract(self):
        if self.contract_template_id:
            template_id = self.contract_template_id
            render_template = self.env['mail.template'].with_context(lang=template_id._context.get('lang'), safe=False)
            generated_field_values = render_template._render_template(
                getattr(template_id, 'body_html'), template_id.model, [self.id], post_process=True)
            render_template = generated_field_values[self.id]
            return render_template

    def action_generate_report_pdf(self):
        for rec in self:
            if rec.contract_template_id:
                report_name = "contract_formats.report_hr_contract"
                pdf = self.env.ref(report_name, False)._render_qweb_pdf(rec.id)[0]
                rec.contract_binary = base64.encodebytes(pdf)
                rec.contract_name = '{} - Contrato.pdf'.format(rec.name or '-')

    def action_generate_massive_report_pdf(self):
        report_name = "contract_formats.report_hr_contract"
        return self.env.ref(report_name).report_action(self)

    def create_action_leads_view(self):
        form = self.env.ref('contract_formats.contract_email_template_preview_form_contract_formats', False)
        action = {
            'name': 'Vista previa contrato',
            'type': "ir.actions.act_window",
            'view_type': "form",
            'view_mode': "form",
            'res_model': 'email_template.preview',
            'views': [(form.id, 'form')],
            'view_id': form.id,
            'target': 'new',
            'context': {
                'template_id': self.contract_template_id.id,
                'default_res_id': self.id
            },
        }
        return action

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(HrContract, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        if view_type == 'form':
            contract_model = self.env.ref('hr_contract.model_hr_contract', False)
            if 'contract_template_id' in res['fields']:
                res['fields']['contract_template_id']['domain'] = [('model_id', '=', contract_model.id)]
        return res

    @api.depends('date_start', 'date_end')
    def compute_service_duration(self):
        for record in self:
            years = months = days = 0
            if record.date_start and record.date_end:
                service_until = record.date_end
                if record.date_start and service_until > record.date_start:
                    service_duration = relativedelta.relativedelta(
                        service_until,
                        record.date_start
                    )
                    years = service_duration.years
                    months = service_duration.months
                    days = service_duration.days
            service_duration = u'{} año(s) {} mes(es) {} día(s)'.format(years, months, days)
            record.service_duration = service_duration

    @api.model
    def _action_update_service_duration_on_contracts(self):
        contracts = self.search([])
        contracts.compute_service_duration()
