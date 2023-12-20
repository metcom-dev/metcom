import json
import logging

from odoo.exceptions import AccessError, MissingError
from odoo.http import request

from odoo import http, SUPERUSER_ID, _
from odoo.addons.portal.controllers.mail import _message_post_helper
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager

_logger = logging.getLogger(__name__)


class CustomerPortalInherit(CustomerPortal):

    def _prepare_portal_layout_values(self):
        values = super(CustomerPortalInherit, self)._prepare_portal_layout_values()
        payslip = request.env['hr.payslip']
        payslip_count = payslip.sudo().search_count([
            ('employee_id.user_id', '=', request.env.user.id),
            ('state', 'not in', ['cancel', 'reject'])
        ])
        values.update({'payslip_count': payslip_count})
        return values

    @http.route(['/my/payslip', '/my/payslip/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_loan(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        payslip_pool = request.sudo().env['hr.payslip']

        domain = [
            ('employee_id.user_id', '=', request.env.user.id),
            ('state', 'not in', ['cancel', 'reject'])
        ]

        searchbar_sortings = {
            'name': {'label': _('Referencia'), 'order': 'number'},
            'stage': {'label': _('Estado'), 'order': 'state'},
        }

        if not sortby:
            sortby = 'name'

        sort_payslip = searchbar_sortings[sortby]['order']

        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        payslip_count = payslip_pool.search_count(domain)

        pager = portal_pager(
            url="/my/payslip",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=payslip_count,
            page=page,
            step=self._items_per_page
        )

        payslip = payslip_pool.search(domain, order=sort_payslip, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_payslip_history'] = payslip.ids[:100]

        values.update({
            'date': date_begin,
            'payslips': payslip.sudo(),
            'page_name': 'payslip',
            'pager': pager,
            'default_url': '/my/payslip',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })
        return request.render("voucher_sending.portal_my_payslip", values)

    @http.route(['/my/payslip/<int:order_id>/accept'], type='json', auth="public", website=True)
    def portal_payslip_accept(self, order_id, report_type=None, access_token=None, message=False, download=False,
                              accept_pay_voucher=False, **kw):
        try:
            access_token = access_token or request.httprequest.args.get('access_token')
            payslip_sudo = self._document_check_access('hr.payslip', order_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        data = json.loads(request.httprequest.data)
        payslip = request.env['hr.payslip'].sudo().search([('id', '=', payslip_sudo.id)])
        if payslip:
            payslip.employee_id.employee_signature = data['params']['signature']

        return {
            'force_refresh': True,
            'redirect_url': payslip.get_portal_url(accept_pay_voucher=True),
        }

    @http.route(['/my/payslip/<int:order_id>'], type='http', auth="public", website=True)
    def portal_payslip_page(self, order_id, report_type=None, access_token=None, message=False, download=False,
                            accept_pay_voucher=False, **kw):
        try:
            payslip_sudo = self._document_check_access('hr.payslip', order_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        if report_type in ('html', 'pdf', 'text'):
            return self._show_report(model=payslip_sudo, report_type=report_type,
                                     report_ref='voucher_payroll.action_report_payslip_voucher_payroll',
                                     download=download)

        if accept_pay_voucher:
            payslip = request.env['hr.payslip'].sudo().search([('id', '=', payslip_sudo.id)])
            if payslip:
                payslip.sudo().write({'status': 'signed'})
                pdf = request.env.ref('voucher_payroll.action_report_payslip_voucher_payroll').with_user(
                    SUPERUSER_ID)._render_qweb_pdf('voucher_payroll.action_report_payslip_voucher_payroll',payslip.id)[0]
                if payslip.employee_id.employee_signature:
                    message_post = 'La boleta fue aceptada y firmada por el empleado %s.' % payslip.employee_id.name
                else:
                    message_post = 'La boleta fue aceptada, pero no se firmo debido que el empleado %s no tiene configurado una firma en su ficha.' % payslip.employee_id.name

                _message_post_helper(
                    'hr.payslip', payslip.id, message_post, attachments=[('%s.pdf' % payslip.name, pdf)],
                    **({'token': access_token} if access_token else {})
                )

        values = {
            'payslip': payslip_sudo,
            'message': message,
            'token': access_token,
            'return_url': '/my/payslip',
            'bootstrap_formatting': True,
            'partner_id': payslip_sudo.employee_id.id,
            'report_type': 'html',
        }
        if payslip_sudo.company_id:
            values['res_company'] = payslip_sudo.company_id
        if payslip_sudo.state not in ('cancel', 'reject'):
            history = request.session.get('my_payslip_history', [])
        else:
            history = request.session.get('my_payslip_history', [])

        values.update(get_records_pager(history, payslip_sudo))
        return request.render('voucher_sending.payslip_portal_template', values)
