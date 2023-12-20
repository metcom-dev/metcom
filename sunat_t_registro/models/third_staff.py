from odoo import api, fields, models
from .reports_third_staff import ThirdStaffRegistroReport
import base64


class HrEmployeThirdStaff(models.Model):
    _name = 'hr.employee.third.staff'
    _description = 'Empleados Personal de Tercero'

    name = fields.Char(string='Nombre')
    contact_id = fields.Many2one('res.partner', string='Contacto')
    type_identification_id = fields.Many2one(
        comodel_name="l10n_latam.identification.type",
        string='Tipo de doc.',
        groups="hr.group_hr_user"
    )
    document_country_id = fields.Many2one(
        comodel_name="res.country",
        string='País emisor del documento',
        groups="hr.group_hr_user"
    )
    identification_id = fields.Char(string='N° identificación')
    date_from = fields.Datetime(string='Desde')
    date_to = fields.Datetime(string='Hasta')
    sctr = fields.Selection(string='SCTR Pensión', selection=[
        ('01', 'ONP'),
        ('02', 'Seguro Privado'),
    ])
    registered_t_register = fields.Boolean(string='Registrado en T-Registro')
    employee_id = fields.Many2one(comodel_name='third.staff')


class ThirdStaff(models.Model):
    _name = 'third.staff'
    _description = 'Personal de Tercero'

    partner_id = fields.Many2one('res.partner', string='Empresas')
    ruc = fields.Char(string='Ruc')
    risk_activity = fields.Boolean(string='Actividad de riesgo')
    date_from = fields.Datetime(string='Desde')
    date_to = fields.Datetime(string='Hasta')
    type_service = fields.Many2one(comodel_name='international.industrial.classification', string='Tipo de servicio')
    employee_third = fields.One2many(comodel_name='hr.employee.third.staff', inverse_name='employee_id', string='Empleados')

    med_filename = fields.Char(string='Nombre archivo .med')
    med_binary = fields.Binary(string='.med')
    ter_filename = fields.Char(string='Nombre archivo .ter')
    ter_binary = fields.Binary(string='.ter')

    @api.onchange('company_id')
    def onchange_vat_ruc(self):
        self.ruc = self.company_id.vat

    def generate_files(self):
        data_med = self._get_data_med()
        data_ter = self._get_data_ter()
        filename = self._get_filename()
        report_file = ThirdStaffRegistroReport(data_med, data_ter, filename, self)

        values = {
            'med_filename': report_file.get_filename('med'),
            'med_binary': base64.encodebytes(report_file.get_content_med() or '\n'.encode()),
            'ter_filename': report_file.get_filename('ter'),
            'ter_binary': base64.encodebytes(report_file.get_content_ter() or '\n'.encode()),
        }
        self.write(values)

    def _get_filename(self):
        company_vat = self.env.company.partner_id.vat or '99999999'
        filename = 'RP_{}'.format(company_vat)
        return filename

    def _get_data_med(self):
        data_med = []

        data_med.append({
            'ruc': self.ruc if self.ruc else '',
            'type_service': self.type_service.code if self.type_service.code else '',
            'date_from': self.date_from.strftime("%d-%m-%Y").replace('-', '/') if self.date_to else '',
            'date_to': self.date_to.strftime("%d-%m-%Y").replace('-', '/') if self.date_to else '',

        })
        return data_med

    def _get_data_ter(self):
        data_ter = []

        for emp in self.employee_third:
            if not emp.registered_t_register:
                data_ter.append({
                    'l10n_pe_vat_code': str(emp.type_identification_id.l10n_pe_vat_code).rjust(2, '0'),
                    'identification_id': emp.identification_id,
                    'cod_pas_only': emp.document_country_id.cod_pas_only if emp.type_identification_id.l10n_pe_vat_code == '7' else '',
                    'ruc': self.ruc if self.ruc else '',
                    'sctr': str(emp.sctr).replace('0', '') if emp.sctr else '',
                })
        return data_ter
