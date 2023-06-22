from .reports_t_registro import TRegistroReport
from odoo import api, fields, models
import base64
from odoo.exceptions import ValidationError
from datetime import datetime


class SunatTRegistro(models.Model):
    _name = "sunat.t.registro"
    _description = "Sunat T registro"

    date_from = fields.Date(string='Fecha de Inicio')
    date_to = fields.Date(string='Fecha de Fin')
    company_id = fields.Many2one(comodel_name='res.company', string='Compañía')

    employees_lines_ids_t = fields.Many2many(comodel_name='hr.employee', relation='employee_lines_t_registro',
                                             string='Empleados')

    esp_filename = fields.Char(string='Nombre archivo .esp')
    esp_binary = fields.Binary(string='.esp')
    edd_filename = fields.Char(string='Nombre archivo .edd')
    edd_binary = fields.Binary(string='.edd')
    idd_filename = fields.Char(string='Nombre archivo .idd')
    idd_binary = fields.Binary(string='.idd')
    ide_filename = fields.Char(string='Nombre archivo .ide')
    ide_binary = fields.Binary(string='.ide')
    tra_filename = fields.Char(string='Nombre archivo .tra')
    tra_binary = fields.Binary(string='.tra')
    pen_filename = fields.Char(string='Nombre archivo .pen')
    pen_binary = fields.Binary(string='.pen')
    pfl_filename = fields.Char(string='Nombre archivo .pfl')
    pfl_binary = fields.Binary(string='.pfl')
    per_filename = fields.Char(string='Nombre archivo .per')
    per_binary = fields.Binary(string='.per Alta')
    per_filename2 = fields.Char(string='Nombre archivo .per')
    per_binary2 = fields.Binary(string='.per Baja')
    cta_filename = fields.Char(string='Nombre archivo .cta')
    cta_binary = fields.Binary(string='.cta')
    edu_filename = fields.Char(string='Nombre archivo .edu')
    edu_binary = fields.Binary(string='.edu')
    est_filename = fields.Char(string='Nombre archivo .est')
    est_binary = fields.Binary(string='.est')
    lug_filename = fields.Char(string='Nombre archivo .lug')
    lug_binary = fields.Binary(string='.lug')

    def generate_files(self):
        data_esp = self._get_data_esp()
        data_edd = self._get_data_edd()
        data_idd = self._get_data_idd()
        data_ide = self._get_data_ide()
        data_tra = self._get_data_tra()
        data_pen = self._get_data_pen()
        data_pfl = self._get_data_pfl()
        data_per = self._get_data_per_alta()
        data_per2 = self._get_data_per_baja()
        data_cta = self._get_data_cta()
        data_edu = self._get_data_edu()
        data_est = self._get_data_est()
        data_lug = self._get_data_lug()
        filename = self._get_filename()
        report_file = TRegistroReport(data_esp, data_edd, data_idd, data_ide, data_tra, data_pen, data_pfl, data_per,
                                      data_per2, data_cta, data_edu, data_est, data_lug, filename, self)

        values = {
            'esp_filename': report_file.get_filename('esp'),
            'esp_binary': base64.encodebytes(report_file.get_content_esp() or '\n'.encode()),
            'edd_filename': report_file.get_filename('edd'),
            'edd_binary': base64.encodebytes(report_file.get_content_edd() or '\n'.encode()),
            'idd_filename': report_file.get_filename('idd'),
            'idd_binary': base64.encodebytes(report_file.get_content_idd() or '\n'.encode()),
            'ide_filename': report_file.get_filename('ide'),
            'ide_binary': base64.encodebytes(report_file.get_content_ide() or '\n'.encode()),
            'tra_filename': report_file.get_filename('tra'),
            'tra_binary': base64.encodebytes(report_file.get_content_tra() or '\n'.encode()),
            'pen_filename': report_file.get_filename('pen'),
            'pen_binary': base64.encodebytes(report_file.get_content_pen() or '\n'.encode()),
            'pfl_filename': report_file.get_filename('pfl'),
            'pfl_binary': base64.encodebytes(report_file.get_content_pfl() or '\n'.encode()),
            'per_filename': report_file.get_filename('per'),
            'per_binary': base64.encodebytes(report_file.get_content_per_alta() or '\n'.encode()),
            'per_filename2': report_file.get_filename('per'),
            'per_binary2': base64.encodebytes(report_file.get_content_per_baja() or '\n'.encode()),
            'cta_filename': report_file.get_filename('cta'),
            'cta_binary': base64.encodebytes(report_file.get_content_cta() or '\n'.encode()),
            'edu_filename': report_file.get_filename('edu'),
            'edu_binary': base64.encodebytes(report_file.get_content_edu() or '\n'.encode()),
            'est_filename': report_file.get_filename('est'),
            'est_binary': base64.encodebytes(report_file.get_content_est() or '\n'.encode()),
            'lug_filename': report_file.get_filename('lug'),
            'lug_binary': base64.encodebytes(report_file.get_content_lug() or '\n'.encode()),
        }
        self.write(values)

    def _get_filename(self):
        company_vat = self.env.company.partner_id.vat or '99999999'
        filename = 'RP_{}'.format(company_vat)
        return filename

    def _get_data_esp(self):
        data_esp = []
        code_file = self.env['ir.config_parameter'].sudo().get_param('hr_contract.risk_activities_sctr')

        for emp in self.employees_lines_ids_t:
            data_esp.append({
                'annexed_establishment': emp.address_home_id.annexed_establishment,
                'parameter': 1 if code_file else 0,
            })
        return data_esp

    def _get_data_edd(self):
        edd_data = []

        for employee in self.employees_lines_ids_t:
            if employee.contract_id.displacemnent:
                edd_data.append({
                    'ruc': employee.contract_id.employer_id.vat,
                    'code_activity': employee.contract_id.given_service.code,
                    'date_init': employee.contract_id.date_from_displacement.strftime("%d-%m-%Y").replace('-',
                                                                                                          '/') if employee.contract_id.date_from_displacement else '',
                    'date_end': employee.contract_id.date_to_displacement.strftime("%d-%m-%Y").replace('-',
                                                                                                       '/') if employee.contract_id.date_to_displacement else '',
                })
            else:
                continue
        return edd_data

    def _get_data_idd(self):
        idd_data = []

        for employee in self.employees_lines_ids_t:
            if employee.contract_id.displacemnent:
                idd_data.append({
                    'ruc': employee.contract_id.employer_id.vat,
                    'annexed_establishment': employee.contract_id.other_annexed.code if employee.contract_id.other_annexed else '    ',
                    'risk_activity': 1 if employee.contract_id.risk_activities else 0,
                })
            else:
                continue
        return idd_data

    def _get_data_ide(self):
        ide_data = []
        for employee in self.employees_lines_ids_t:
            gender = '1' if employee.gender == 'male' else '2'
            essalud_indicator = '1' if employee.address_home_id.indicator_essalud == '01' else '2'

            ide_data.append({
                '0': '0',
                'l10n_pe_vat_code': employee.type_identification_id.l10n_pe_vat_code,
                'identification_id': employee.identification_id,
                'cod_sunat_res_country': employee.document_country_id.cod_pas_only,
                'birthday': employee.birthday.strftime("%m-%m-%Y").replace('-', '/') if employee.birthday else '',
                'lastname': employee.lastname,
                'secondname': employee.secondname,
                'firstname': employee.firstname,
                'gender': gender,
                'nacionality_code': employee.country_id.nacionality_code_rc,
                'mobile': employee.address_home_id.mobile,
                'email': employee.address_home_id.email,
                'road_type_code': str(employee.address_home_id.road_type.code).rjust(2, '0'),
                'road_type_name': employee.address_home_id.road_name,
                'road_number': employee.address_home_id.road_number,
                'road_departament': employee.address_home_id.road_departament,
                'road_inside': employee.address_home_id.road_inside,
                'road_mz': employee.address_home_id.road_mz,
                'road_batch': employee.address_home_id.road_batch,
                'road_km': employee.address_home_id.road_km,
                'road_block': employee.address_home_id.road_block,
                'road_stage': employee.address_home_id.road_stage,
                'zone_type': employee.address_home_id.zone_type.code,
                'zone_name': employee.address_home_id.zone_name,
                'zone_reference': employee.address_home_id.zone_reference,
                'zone_ubigeo': employee.address_home_id.zone_ubigeo.code,
                'road_type_2': str(employee.address_home_id.road_type_2.code).rjust(2, '0'),
                'road_name_2': employee.address_home_id.road_name_2,
                'road_number_2': employee.address_home_id.road_number_2,
                'road_departament_2': employee.address_home_id.road_departament_2,
                'road_inside_2': employee.address_home_id.road_inside_2,
                'road_mz_2': employee.address_home_id.road_mz_2,
                'road_batch_2': employee.address_home_id.road_batch_2,
                'road_km_2': employee.address_home_id.road_km_2,
                'road_block_2': employee.address_home_id.road_block_2,
                'road_stage_2': employee.address_home_id.road_stage_2,
                'zone_type_2': employee.address_home_id.zone_type_2.code,
                'zone_name_2': employee.address_home_id.zone_name_2,
                'zone_reference_2': employee.address_home_id.zone_reference_2,
                'zone_ubigeo_2': employee.address_home_id.zone_ubigeo_2.code,
                'indicator_essalud': essalud_indicator,
            })

        return ide_data

    def _get_data_tra(self):
        tra_data = []
        for employee in self.employees_lines_ids_t:
            int_part, dec_part = str(employee.contract_id.wage).split('.')
            tra_data.append({
                '0': '0',
                'l10n_pe_vat_code': employee.type_identification_id.l10n_pe_vat_code,
                'identification_id': employee.identification_id,
                'cod_sunat_res_country': employee.document_country_id.cod_pas_only if employee.type_identification_id.l10n_pe_vat_code == '7' else '',
                'labor_regime_id': employee.contract_id.labor_regime_id.code,
                'academic_degree_id': str(employee.academic_degree_id.code).rjust(2, '0'),
                'work_occupation_id': employee.contract_id.work_occupation_id.code,
                'disability': '1' if employee.disability else '0',
                'cuspp': str(employee.cuspp).rjust(2, '0'),
                'sctr': int(employee.sctr) if employee.sctr else '',
                'labor_condition_id': str(employee.contract_id.labor_condition_id.code).rjust(2, '0'),
                'atypical_cumulative_day': '1' if employee.contract_id.atypical_cumulative_day else '0',
                'maximum_working_day': '1' if employee.contract_id.maximum_working_day else '0',
                'nocturnal_schedule': '1' if employee.contract_id.nocturnal_schedule else '0',
                'unionized': '1' if employee.contract_id.unionized else '0',
                'periodicity': int(employee.contract_id.periodicity) if employee.contract_id.periodicity else '',
                'wage': int_part + '.' + dec_part.ljust(2, '0'),
                'situation': employee.situation,
                'rent_category': '1' if employee.rent_category else '0',
                'special_situation_id': employee.contract_id.special_situation_id.code,
                'payment_type_id': employee.contract_id.payment_type_id.code,
                'work_category': str(employee.contract_id.work_category.code),
                'double_taxation': employee.double_taxation,
            })
        return tra_data

    def _get_data_pen(self):
        pen_data = []

        for employee in self.employees_lines_ids_t:
            if employee.contract_id.worker_type_pensioner_provider:
                pen_data.append({
                    'type_identification_id': str(employee.type_identification_id.l10n_pe_vat_code).rjust(2,
                                                                                                          '0') if employee.type_identification_id.l10n_pe_vat_code else '',
                    'cod_sunat_res_country': employee.document_country_id.cod_pas_only if employee.document_country_id.cod_pas_only else '',
                    'worker_type_pensioner_provider': employee.contract_id.worker_type_pensioner_provider.code if employee.contract_id.worker_type_pensioner_provider else '',
                    'identification_id': employee.identification_id if employee.identification_id else '',
                    'pension_system_id': str(employee.pension_system_id.code).rjust(2,
                                                                                    '0') if employee.pension_system_id.code else '',
                    'cuspp': str(employee.cuspp).rjust(2, '0') if employee.cuspp else '',
                    'payment_type_id': employee.contract_id.payment_type_id.code if employee.contract_id.payment_type_id.code else '',
                })
            else:
                continue
        return pen_data

    def _get_data_pfl(self):
        pfl_data = []

        for employee in self.employees_lines_ids_t:
            if employee.contract_id.is_practitioner:
                pfl_data.append({
                    'type_identification_id': str(employee.type_identification_id.l10n_pe_vat_code).rjust(2,
                                                                                                          '0') if employee.type_identification_id.l10n_pe_vat_code else '',
                    'cod_sunat_res_country': employee.identification_id if employee.identification_id else '',
                    'type_formative_modality': employee.contract_id.type_formative_modality.code if employee.contract_id.type_formative_modality else '',
                    'health_insurance_contract': str(employee.contract_id.health_insurance_contract).replace('0',
                                                                                                             '') if employee.contract_id.health_insurance_contract else '',
                    'academic_degree_id': str(employee.academic_degree_id.code).rjust(2,
                                                                                      '0') if employee.academic_degree_id.code else '',
                    'occupation_training_modality': employee.contract_id.occupation_training_modality.code if employee.contract_id.occupation_training_modality else '',
                    'mother_responsability': '1' if employee.contract_id.mother_responsability else '0',
                    'disability': '1' if employee.disability else '0',
                    'type_professional_center': str(employee.contract_id.type_professional_center).replace('0',
                                                                                                           '') if employee.contract_id.type_professional_center else '',
                    'nocturnal_schedule': '1' if employee.contract_id.nocturnal_schedule else '0',
                })
            else:
                continue
        return pfl_data

    def _get_data_per_alta(self):
        per_data_alta = []
        if not self.employees_lines_ids_t:
            employees = self.env['hr.employee'].search([('company_id', '=', self.company_id.id)])
            for employee in employees:
                if self.date_from and self.date_to and employee.contract_id.first_contract_date and self.date_from <= employee.contract_id.first_contract_date <= self.date_to:
                    per_data_alta.append({
                        'type_identification_id': str(employee.type_identification_id.l10n_pe_vat_code).rjust(2,
                                                                                                              '0') if employee.type_identification_id.l10n_pe_vat_code else '',
                        'identification_id': employee.identification_id if employee.identification_id else '',
                        'cod_sunat_res_country': employee.document_country_id.cod_pas_only if employee.document_country_id.cod_pas_only else '',
                        'category_employee': employee.category_employee if employee.category_employee else '',
                        'date_end': employee.contract_id.date_end.strftime("%d-%m-%Y").replace('-','/') if employee.contract_id.reason_low_id and employee.contract_id.date_end else '',
                        'date_start': employee.contract_id.date_start.strftime("%d-%m-%Y").replace('-', '/') if employee.contract_id.date_start and employee.contract_id.date_start  else '',
                        'worker_type_pensioner_provider': employee.contract_id.worker_type_pensioner_provider.code if employee.contract_id.worker_type_pensioner_provider else '',
                        'bool': True if employee.pension_sctr else False,
                        'health_regime': employee.health_regime_id.code if employee.health_regime_id.code else '',
                        'eps_salud': employee.eps_services_propios if employee.health_regime_id.code == '01' or employee.health_regime_id.code == '03' else '',
                        'pension_system': employee.pension_system_id.code if employee.pension_system_id.code else '',
                        'sctr_salud': employee.sctr_salud.rjust(2, '0') if employee.sctr_salud  else '',

                    })
        else:
            for employee in self.employees_lines_ids_t:
                per_data_alta.append({
                    'type_identification_id': str(employee.type_identification_id.l10n_pe_vat_code).rjust(2,
                                                                                                          '0') if employee.type_identification_id.l10n_pe_vat_code else '',
                    'identification_id': employee.identification_id if employee.identification_id else '',
                    'cod_sunat_res_country': employee.document_country_id.cod_pas_only if employee.document_country_id.cod_pas_only else '',
                    'category_employee': employee.category_employee if employee.category_employee else '',
                    'date_end': employee.contract_id.date_end.strftime("%d-%m-%Y").replace('-','/') if employee.contract_id.reason_low_id and employee.contract_id.date_end else '',
                    'date_start': employee.contract_id.date_start.strftime("%d-%m-%Y").replace('-', '/') if employee.contract_id.reason_low_id and employee.contract_id.date_start else '',
                    'worker_type_pensioner_provider': employee.contract_id.worker_type_pensioner_provider.code if employee.contract_id.worker_type_pensioner_provider else '',
                    'bool': employee.pension_sctr if employee.pension_sctr else '',
                    'health_regime': employee.health_regime_id.code if employee.health_regime_id.code else '',
                    'eps_salud': employee.eps_services_propios if employee.health_regime_id.code == '01' or employee.health_regime_id.code == '03' else '',
                    'pension_system': employee.pension_system_id.code if employee.pension_system_id.code else '',
                    'sctr_salud': employee.sctr_salud.rjust(2, '0') if employee.sctr_salud else '',
                })

        return per_data_alta

    def query_data_per_baja(self):
        query = """ 
        SELECT DISTINCT ON (e.id)
        e.id,
        e.name,
        e.identification_id as identification,
        llit.l10n_pe_vat_code as vat_code,
        rc.cod_pas_only as cod_pas_only,
        e.category_employee as category_emp,
        hc.date_end  as date_final,
        lr.code as code_low,
        MAX(hc.create_date)
        FROM hr_employee e
        LEFT JOIN hr_contract hc ON  e.id= hc.employee_id
        LEFT JOIN l10n_latam_identification_type llit on llit.id=e.type_identification_id
        LEFT JOIN  res_country   rc  on rc.id=e.country_id
        LEFT JOIN low_reason lr  on lr.id=hc.reason_low_id
        WHERE (hc.company_id ='{company_id}') and 
        (hc.date_end BETWEEN '{date_start}' and '{date_end}')
        GROUP  BY e.id,e.identification_id,e.name,llit.l10n_pe_vat_code,rc.cod_pas_only,
        e.category_employee,hc.date_end,lr.code
        """.format(
            company_id=self.company_id.id,
            date_start=self.date_from,
            date_end=self.date_to
        )
        try:
            self.env.cr.execute(query)
            data_query = self.env.cr.dictfetchall()
            return data_query
        except Exception as error:
            raise ValidationError(f'Error al ejecutar la queries, comunicar al administrador: \n {error}')

    def _get_data_per_baja(self):
        per_data_baja = []
        if not self.employees_lines_ids_t:
            data_query = self.query_data_per_baja()
            for emp in data_query:
                per_data_baja.append({
                    'type_identification_id': emp.get('vat_code', '').zfill(2) if emp.get('vat_code') else '',
                    'identification_id':emp.get('identification') if emp.get('identification') else '',
                    'cod_sunat_res_country': emp.get('cod_pas_only') if emp.get('cod_pas_only') else '',
                    'category_employee': emp.get('category_emp') if emp.get('category_emp') else '',
                    'date_end': emp.get('date_final').strftime("%d-%m-%Y").replace('-', '/')  if emp.get('code_low') and emp.get('date_final') else '',
                    'reason_low': emp.get('code_low').rjust(2, '0') if emp.get('code_low') else '',
                })

        else:
            for employee in self.employees_lines_ids_t:
                per_data_baja.append({
                    'type_identification_id': str(employee.type_identification_id.l10n_pe_vat_code).rjust(2,
                                                                                                          '0') if employee.type_identification_id.l10n_pe_vat_code else '',
                    'identification_id': employee.identification_id if employee.identification_id else '',
                    'cod_sunat_res_country': employee.document_country_id.cod_pas_only if employee.document_country_id.cod_pas_only else '',
                    'category_employee': employee.category_employee if employee.category_employee else '',
                    'date_end': employee.contract_id.date_end.strftime("%d-%m-%Y").replace('-', '/')  if employee.contract_id.reason_low_id and employee.contract_id.date_end else '',
                    'reason_low': employee.contract_id.reason_low_id.code.rjust(2, '0') if employee.contract_id.reason_low_id.code else '',
                })
        return per_data_baja

    def _get_data_cta(self):
        cta_data = []
        number_acc = None
        cta_code = None
        for employee in self.employees_lines_ids_t:
            data_emp = self.env['res.partner.bank'].search(
                [('partner_id', '=', employee.address_home_id.id), '|', ('company_id', '=', False),
                 ('company_id', '=', employee.company_id.id)])
            for x in data_emp:
                if employee.address_home_id.id == x.partner_id.id:
                    if x.acc_type == 'wage':
                        number_acc = x.acc_number
                        cta_code = x.type_bank_code

            cta_data.append({
                'type_identification_id': str(employee.type_identification_id.l10n_pe_vat_code).rjust(2,
                                                                                                      '0') if employee.type_identification_id.l10n_pe_vat_code else '',
                'identification_id': employee.identification_id if employee.identification_id else '',
                'country_cod': employee.document_country_id.code if employee.type_identification_id.l10n_pe_vat_code == '7' else '',
                'cta_sueldo': cta_code,
                'nro_cta': number_acc,
            })
        return cta_data

    def _get_data_edu(self):
        edu_data = []

        for employee in self.employees_lines_ids_t:
            edu_data.append({
                'type_identification_id': str(employee.type_identification_id.l10n_pe_vat_code).rjust(2,
                                                                                                      '0') if employee.type_identification_id.l10n_pe_vat_code else '',
                'identification_id': employee.identification_id if employee.identification_id else '',
                'cod_sunat_res_country': employee.document_country_id.cod_pas_only if employee.document_country_id.cod_pas_only else '',
                'sit_edu': employee.academic_degree_id.code if employee.academic_degree_id.code == '11' or employee.academic_degree_id.code == '13' else '',
                'bool_edu': '1' if employee.edu_name_id else '0',
                'code_edu': employee.edu_name_id.code if employee.edu_name_id.code else '',
                'code_career': employee.edu_career_id.code.zfill(6) if employee.edu_career_id.code else '',
                'edu_year': employee.edu_year_id.name if employee.edu_year_id.name else '',
            })
        return edu_data

    def _get_data_est(self):
        est_data = []

        if self.employees_lines_ids_t:
            for employee in self.employees_lines_ids_t:
                est_data.append({
                    'type_identification_id': str(employee.type_identification_id.l10n_pe_vat_code).rjust(2,
                                                                                                          '0') if employee.type_identification_id.l10n_pe_vat_code else '',
                    'identification_id': employee.identification_id if employee.identification_id else '',
                    'cod_sunat_res_country': employee.document_country_id.cod_pas_only if employee.document_country_id.cod_pas_only else '',
                    'cod_add': employee.address_id.vat if employee.address_id.vat else '',
                    'cod_anex': employee.other_annexed[0].code if employee.other_annexed else '    ',

                })
            return est_data
        else:
            employees_t = []
            employess_db = self.env['hr.employee'].search([])
            for empl in employess_db:
                for contract in empl.contract_ids:
                    if contract.date_start >= self.date_from and contract.date_start <= self.date_to:
                        employees_t.append(empl)
                        break

            for employee in employees_t:
                est_data.append({
                    'type_identification_id': str(employee.type_identification_id.l10n_pe_vat_code).rjust(2,
                                                                                                          '0') if employee.type_identification_id.l10n_pe_vat_code else '',
                    'identification_id': employee.identification_id if employee.identification_id else '',
                    'cod_sunat_res_country': employee.document_country_id.cod_pas_only if employee.document_country_id.cod_pas_only else '',
                    'cod_add': employee.address_id.vat if employee.address_id.vat else '',
                    'cod_anex': employee.other_annexed[0].code if employee.other_annexed else '    ',

                })
            return est_data

    def _get_data_lug(self):
        lug_data = []

        for employee in self.employees_lines_ids_t:
            lug_data.append({
                'type_identification_id': str(employee.type_identification_id.l10n_pe_vat_code).rjust(2,
                                                                                                      '0') if employee.type_identification_id.l10n_pe_vat_code else '',
                'identification_id': employee.identification_id if employee.identification_id else '',
                'cod_sunat_res_country': employee.document_country_id.cod_pas_only if employee.document_country_id.cod_pas_only else '',
                'category_emp': employee.category_employee if employee.category_employee else '',
                'cod_annex': employee.company_id.l10n_pe_edi_address_type_code if employee.company_id.l10n_pe_edi_address_type_code else '',
            })
        return lug_data
