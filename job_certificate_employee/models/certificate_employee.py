from odoo import models, fields, api
from datetime import datetime


class CertificateEmployee(models.Model):
    _inherit = 'hr.employee'

    date_today = fields.Char(string='Fecha', compute='_date_today')

    def search_employee(self):
        return self.env['hr.employee'].search([('is_employer', '=', True)], limit=1)

    def _date_today(self):
        now = datetime.now()
        date = now.strftime('%d de %B de %Y')
        self.date_today = date

    def print_report(self):
        return self.env.ref('job_certificate_employee.report_job_certification_employee').report_action(docids=None)
