from odoo import api, fields, models
from .reports_right_holders import ReportRightHolders
import base64


class HrEmployeRightHolders(models.Model):
    _name = 'hr.employee.right.holders'
    _description = 'Derechohabientes de los empleados'
    start_date = fields.Date(string='Fecha de inicio', required=True)
    end_date = fields.Date(string='Fecha fin', required=True)

    company_id = fields.Many2one(
        required=True,
        comodel_name='res.company',
        string="Compañia",
    )

    type = fields.Selection(
        string='Tipo',
        selection=[
            ('01', 'Alta'),
            ('02', 'Baja'),
        ],
        required=True
    )
    employee_id = fields.Many2one(
        comodel_name='hr.employee',
        string='Empleado',
        domain="[('company_id', '=', company_id)]"
    )
    right_holders = fields.Many2many(
        string="Derechohabientes",
        comodel_name="hr.employee.relative",
        domain="[('right_holder', '=', True), ('employee_id', '=', employee_id)]"
    )

    txt_filename = fields.Char(string='Filaname .txt')
    txt_binary = fields.Binary(string='Reporte .TXT')

    def get_data_01(self, right_holders):
        data = []

        for right_holder in right_holders:
            data.append({
                'type_identification_employee_code': self.get_two_digits(right_holder.employee_id.type_identification_id.l10n_pe_vat_code),
                'identification_employee_num': right_holder.employee_id.identification_id if right_holder.employee_id.identification_id else '',
                'type_identification_code': self.get_two_digits(right_holder.type_identification_id.l10n_pe_vat_code),
                'identification_num': right_holder.identification_id if right_holder.identification_id else '',
                'code_pas_only': right_holder.document_country_id.cod_pas_only if right_holder.document_country_id else '',
                'date_of_birth': right_holder.date_of_birth.strftime("%d-%m-%Y").replace('-', '/') if right_holder.date_of_birth else '',
                'first_lastname': right_holder.first_lastname if right_holder.first_lastname else '',
                'second_lastname': right_holder.second_lastname if right_holder.second_lastname else '',
                'name': right_holder.name,
                'gender': self.get_gender(right_holder.gender),
                'relation_type': right_holder.relation_type if right_holder.relation_type else '',
                'doc_acreditation': right_holder.doc_acreditation if right_holder.doc_acreditation else '',
                'n_doc_acred': right_holder.n_doc_acred if right_holder.n_doc_acred else '',
                'month_pregnant': right_holder.month_pregnant.strftime('%m%Y') if right_holder.month_pregnant else '',

                # first address
                'road_type_code': self.get_two_digits(right_holder.address_home_id.road_type.code),
                'road_name': self.get_text_with_maxlen(right_holder.address_home_id.road_name, 20),
                'road_number': self.get_text_with_maxlen(right_holder.address_home_id.road_number, 4),
                'road_departament': self.get_text_with_maxlen(right_holder.address_home_id.road_departament, 4),
                'road_inside': self.get_text_with_maxlen(right_holder.address_home_id.road_inside, 4),
                'road_mz': self.get_text_with_maxlen(right_holder.address_home_id.road_mz, 4),
                'road_batch': self.get_text_with_maxlen(right_holder.address_home_id.road_batch, 4),
                'road_km': self.get_text_with_maxlen(right_holder.address_home_id.road_km, 4),
                'road_block': self.get_text_with_maxlen(right_holder.address_home_id.road_block, 4),
                'road_stage': self.get_text_with_maxlen(right_holder.address_home_id.road_stage, 4),
                'zone_type_code': self.get_text_with_maxlen(right_holder.address_home_id.zone_type.code, 2),
                'zone_name': self.get_text_with_maxlen(right_holder.address_home_id.zone_name, 20),
                'zone_reference': self.get_text_with_maxlen(right_holder.address_home_id.zone_reference, 40),
                'zone_ubigeo_code': self.get_text_with_maxlen(right_holder.address_home_id.zone_ubigeo.code, 6),
                # second address
                'road_type_code_2': self.get_text_with_maxlen(right_holder.address_home_id.road_type_2.code, 2),
                'road_name_2': self.get_text_with_maxlen(right_holder.address_home_id.road_name_2, 20),
                'road_number_2': self.get_text_with_maxlen(right_holder.address_home_id.road_number_2, 4),
                'road_departament_2': self.get_text_with_maxlen(right_holder.address_home_id.road_departament_2, 4),
                'road_inside_2': self.get_text_with_maxlen(right_holder.address_home_id.road_inside_2, 4),
                'road_mz_2': self.get_text_with_maxlen(right_holder.address_home_id.road_mz_2, 4),
                'road_batch_2': self.get_text_with_maxlen(right_holder.address_home_id.road_batch_2, 4),
                'road_km_2': self.get_text_with_maxlen(right_holder.address_home_id.road_km_2, 4),
                'road_block_2': self.get_text_with_maxlen(right_holder.address_home_id.road_block_2, 4),
                'road_stage_2': self.get_text_with_maxlen(right_holder.address_home_id.road_stage_2, 4),
                'zone_type_code_2': self.get_text_with_maxlen(right_holder.address_home_id.zone_type_2.code, 2),
                'zone_name_2': self.get_text_with_maxlen(right_holder.address_home_id.zone_name_2, 20),
                'zone_reference_2': self.get_text_with_maxlen(right_holder.address_home_id.zone_reference_2, 40),
                'zone_ubigeo_code_2': self.get_text_with_maxlen(right_holder.address_home_id.zone_ubigeo_2.code, 6),

                # Extra information
                'indicator_essalud': self.get_indicador(right_holder.address_home_id.indicator_essalud),
                'phone': self.get_phone(right_holder.address_home_id.phone),
                'email': right_holder.address_home_id.email if right_holder.address_home_id.email else '',
            })

        return data

    def get_data_02(self, right_holders):
        data = []

        for right_holder in right_holders:
            data.append({
                'type_identification_employee_code': self.get_two_digits(right_holder.employee_id.type_identification_id.l10n_pe_vat_code),
                'identification_employee_num': right_holder.employee_id.identification_id if right_holder.employee_id.identification_id else '',
                'type_identification_code': self.get_two_digits(right_holder.type_identification_id.l10n_pe_vat_code),
                'identification_num': right_holder.identification_id if right_holder.identification_id else '',
                'code_pas_only': right_holder.document_country_id.cod_pas_only if right_holder.document_country_id else '',
                'date_of_birth': right_holder.date_of_birth.strftime("%d-%m-%Y").replace('-', '/') if right_holder.date_of_birth else '',
                'first_lastname': right_holder.first_lastname if right_holder.first_lastname else '',
                'second_lastname': right_holder.second_lastname if right_holder.second_lastname else '',
                'name': right_holder.name,
                'relation_type': right_holder.relation_type if right_holder.relation_type else '',
                'low_date': right_holder.low_date.strftime("%d-%m-%Y").replace('-', '/') if right_holder.low_date else '',
                'reason_leave': right_holder.reason_leave if right_holder.reason_leave else '',
            })

        return data

    def get_data(self, right_holders, type):

        if type == 1:
            return self.get_data_01(right_holders)
        elif type == 2:
            return self.get_data_02(right_holders)

    def get_two_digits(self, code):
        if code == False:
            return ''
        elif len(code) == 1:
            return '0' + code
        else:
            return code

    def get_gender(self, gender):
        if gender == 'male':
            return '1'
        elif gender == 'femle':
            return '2'
        else:
            return ''

    def get_text_with_maxlen(self, text, maxlen):
        if text == False:
            return ''
        elif len(text) > maxlen:
            return text[:maxlen - 1]
        else:
            return text

    def get_indicador(self, ind):
        if ind == '01':
            return '1'
        elif ind == '02':
            return '2'
        else:
            return ''

    def get_phone(self, number):
        if number == False:
            return ''
        elif '+51' == number[:3]:
            return number[3:]
        else:
            return number

    def generate_files(self):

        if self.type == '01':

            if self.right_holders:
                right_holders_ids = self.right_holders

            else:
                right_holders_ids = self.env['hr.employee.relative'].search([
                    ('high_date', '>=', self.start_date),
                    ('high_date', '<=', self.end_date),
                    ('right_holder', '=', True),
                    ('employee_id.company_id.id', '=', self.company_id.id),
                ])

            data = self.get_data(right_holders_ids, 1)
            report_txt = ReportRightHolders(self, data, 1)

        elif self.type == '02':

            if self.right_holders:
                right_holders_ids = self.right_holders

            else:
                right_holders_ids = self.env['hr.employee.relative'].search([
                    ('low_date', '>=', self.start_date),
                    ('low_date', '<=', self.end_date),
                    ('right_holder', '=', True),
                    ('employee_id.company_id.id', '=', self.company_id.id),
                ])
            data = self.get_data(right_holders_ids, 2)
            report_txt = ReportRightHolders(self, data, 2)

        values_content_txt = report_txt.get_content()
        value = {
            'txt_binary': base64.b64encode(values_content_txt.encode() or '\n'.encode()),
            'txt_filename': report_txt.get_filename()
        }

        self.write(value)
