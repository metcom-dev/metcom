class TRegistroReport(object):

    def __init__(self, esp_data, edd_data, idd_data, ide_data, tra_data, pen_data, pfl_data, per_data_alta, per_data_baja, cta_data, edu_data, est_data, lug_data, filename, obj):
        self.esp_data = esp_data
        self.edd_data = edd_data
        self.idd_data = idd_data
        self.ide_data = ide_data
        self.tra_data = tra_data
        self.pen_data = pen_data
        self.pfl_data = pfl_data
        self.per_data_alta = per_data_alta
        self.per_data_baja = per_data_baja
        self.cta_data = cta_data
        self.edu_data = edu_data
        self.est_data = est_data
        self.lug_data = lug_data
        self.filename = filename
        self.obj = obj

    def get_filename(self, file_type):
        if file_type == 'esp':
            filename = '{}.esp'.format(self.filename)
        elif file_type == 'edd':
            filename = '{}.edd'.format(self.filename)
        elif file_type == 'idd':
            filename = '{}.idd'.format(self.filename)
        elif file_type == 'tra':
            filename = '{}.tra'.format(self.filename)
        elif file_type == 'pen':
            filename = '{}.pen'.format(self.filename)
        elif file_type == 'pfl':
            filename = '{}.pfl'.format(self.filename)
        elif file_type == 'per':
            filename = '{}.per'.format(self.filename)
        elif file_type == 'cta':
            filename = '{}.cta'.format(self.filename)
        elif file_type == 'edu':
            filename = '{}.edu'.format(self.filename)
        elif file_type == 'est':
            filename = '{}.est'.format(self.filename)
        elif file_type == 'lug':
            filename = '{}.lug'.format(self.filename)
        else:
            filename = '{}.ide'.format(self.filename)
        return filename

    def get_content_esp(self):
        raw = ''
        template = '{annexed_establishment}|{parameter}\r\n'

        for value in self.esp_data:
            raw += template.format(
                annexed_establishment=value['annexed_establishment'],
                parameter=value['parameter']
            )
        return raw.encode('utf8')

    def get_content_edd(self):
        raw = ''
        template = '{ruc}|{code_activity}|{date_init}|{date_end}\r\n'

        for value in self.edd_data:
            raw += template.format(
                ruc=value['ruc'],
                code_activity=value['code_activity'],
                date_init=value['date_init'],
                date_end=value['date_end'],
            )
        return raw.encode('utf8')

    def get_content_idd(self):
        raw = ''
        template = '{ruc}|{annexed_establishment}|{risk_activity}\r\n'

        for value in self.idd_data:
            raw += template.format(
                ruc=value['ruc'],
                annexed_establishment=value['annexed_establishment'],
                risk_activity=value['risk_activity'],
            )
        return raw.encode('utf8')

    def get_content_ide(self):
        raw = ''
        template = '{cero}{l10n_pe_vat_code}|{identification_id}|' \
                   '{cod_sunat_res_country}|{birthday}|{lastname}|' \
                   '{secondname}|{firstname}|{gender}|' \
                   '{nacionality_code}||{mobile}|{email}|' \
                   '{road_type_code}|{road_type_name}|{road_number}|' \
                   '{road_departament}|{road_inside}|{road_mz}|' \
                   '{road_batch}|{road_km}|{road_block}|{road_stage}|' \
                   '{zone_type}|{zone_name}|{zone_reference}|' \
                   '{zone_ubigeo}|{road_type_2}|{road_name_2}|' \
                   '{road_number_2}|{road_departament_2}|{road_inside_2}|' \
                   '{road_mz_2}|{road_batch_2}|{road_km_2}|' \
                   '{road_block_2}|{road_stage_2}|{zone_type_2}|' \
                   '{zone_name_2}|{zone_reference_2}|{zone_ubigeo_2}|' \
                   '{indicator_essalud}\r\n'

        for value in self.ide_data:
            for key, val in value.items():
                if val == False or val == 'False' or not val:
                    value[key] = ''
            raw += template.format(
                cero=value['0'],
                l10n_pe_vat_code=value['l10n_pe_vat_code'],
                identification_id=value['identification_id'],
                cod_sunat_res_country=value['cod_sunat_res_country'],
                birthday=value['birthday'],
                lastname=value['lastname'],
                secondname=value['secondname'],
                firstname=value['firstname'],
                gender=value['gender'],
                nacionality_code=value['nacionality_code'],
                mobile=value['mobile'],
                email=value['email'],
                road_type_code=value['road_type_code'],
                road_type_name=value['road_type_name'],
                road_number=value['road_number'],
                road_departament=value['road_departament'],
                road_inside=value['road_inside'],
                road_mz=value['road_mz'],
                road_batch=value['road_batch'],
                road_km=value['road_km'],
                road_block=value['road_block'],
                road_stage=value['road_stage'],
                zone_type=value['zone_type'],
                zone_name=value['zone_name'],
                zone_reference=value['zone_reference'],
                zone_ubigeo=value['zone_ubigeo'],
                road_type_2=value['road_type_2'],
                road_name_2=value['road_name_2'],
                road_number_2=value['road_number_2'],
                road_departament_2=value['road_departament_2'],
                road_inside_2=value['road_inside_2'],
                road_mz_2=value['road_mz_2'],
                road_batch_2=value['road_batch_2'],
                road_km_2=value['road_km_2'],
                road_block_2=value['road_block_2'],
                road_stage_2=value['road_stage_2'],
                zone_type_2=value['zone_type_2'],
                zone_name_2=value['zone_name_2'],
                zone_reference_2=value['zone_reference_2'],
                zone_ubigeo_2=value['zone_ubigeo_2'],
                indicator_essalud=value['indicator_essalud'],
            )

        return raw.encode('utf8')

    def get_content_tra(self):
        raw = ''
        template = '{cero}{l10n_pe_vat_code}|{identification_id}|{cod_sunat_res_country}|' \
                   '{labor_regime_id}|{academic_degree_id}|{work_occupation_id}|{disability}|' \
                   '{cuspp}|{sctr}|{labor_condition_id}|{atypical_cumulative_day}|{nocturnal_schedule}|' \
                   '{nocturnal_schedule}|{unionized}|{periodicity}|{wage}|{situation}|{rent_category}|' \
                   '{special_situation_id}|{payment_type_id}|{work_category}|{double_taxation}||\r\n'

        for value in self.tra_data:
            for key, val in value.items():
                if val == False or val == 'False' or not val:
                    value[key] = ''
            raw += template.format(
                cero=value['0'],
                l10n_pe_vat_code=value['l10n_pe_vat_code'],
                identification_id=value['identification_id'],
                cod_sunat_res_country=value['cod_sunat_res_country'],
                labor_regime_id=value['labor_regime_id'],
                academic_degree_id=value['academic_degree_id'],
                work_occupation_id=value['work_occupation_id'],
                disability=value['disability'],
                cuspp=value['cuspp'],
                sctr=value['sctr'],
                labor_condition_id=value['labor_condition_id'],
                atypical_cumulative_day=value['atypical_cumulative_day'],
                maximum_working_day=value['maximum_working_day'],
                nocturnal_schedule=value['nocturnal_schedule'],
                unionized=value['unionized'],
                periodicity=value['periodicity'],
                wage=value['wage'],
                situation=value['situation'],
                rent_category=value['rent_category'],
                special_situation_id=value['special_situation_id'],
                payment_type_id=value['payment_type_id'],
                work_category=value['work_category'],
                double_taxation=value['double_taxation'],
            )
        return raw.encode('utf8')

    def get_content_pen(self):
        raw = ''
        template = '{type_identification_id}|{cod_sunat_res_country}|' \
                   '{worker_type_pensioner_provider}|{identification_id}|' \
                   '{pension_system_id}|{cuspp}|{payment_type_id}\r\n'

        for value in self.pen_data:
            raw += template.format(
                type_identification_id=value['type_identification_id'],
                cod_sunat_res_country=value['cod_sunat_res_country'],
                worker_type_pensioner_provider=value['worker_type_pensioner_provider'],
                identification_id=value['identification_id'],
                pension_system_id=value['pension_system_id'],
                cuspp=value['cuspp'],
                payment_type_id=value['payment_type_id'],
            )
        return raw.encode('utf8')

    def get_content_pfl(self):
        raw = ''
        template = '{type_identification_id}|{cod_sunat_res_country}|' \
                   '{type_formative_modality}|{health_insurance_contract}|' \
                   '{academic_degree_id}|{occupation_training_modality}|' \
                   '{mother_responsability}|{disability}|' \
                   '{type_professional_center}|{nocturnal_schedule}\r\n'

        for value in self.pfl_data:
            raw += template.format(
                type_identification_id=value['type_identification_id'],
                cod_sunat_res_country=value['cod_sunat_res_country'],
                type_formative_modality=value['type_formative_modality'],
                health_insurance_contract=value['health_insurance_contract'],
                academic_degree_id=value['academic_degree_id'],
                occupation_training_modality=value['occupation_training_modality'],
                mother_responsability=value['mother_responsability'],
                disability=value['disability'],
                type_professional_center=value['type_professional_center'],
                nocturnal_schedule=value['nocturnal_schedule'],
            )
        return raw.encode('utf8')

    def get_content_per_alta(self):
        raw = ''
        template = '{type_identification_id}|{identification_id}|{cod_sunat_res_country}|{category_employee}|1|{date_start}||||\n' \
                   '{type_identification_id}|{identification_id}|{cod_sunat_res_country}|{category_employee}|2|{date_start}||{worker_type_pensioner_provider}||\n' \
                   '{type_identification_id}|{identification_id}|{cod_sunat_res_country}|{category_employee}|3|{date_start}||{health_regime}|{eps_salud}|\n' \
                   '{type_identification_id}|{identification_id}|{cod_sunat_res_country}|{category_employee}|4|{date_start}||{pension_system}||\n'
        for value in self.per_data_alta:
            if value['bool']:
                template+='{type_identification_id}|{identification_id}|{cod_sunat_res_country}|{category_employee}|5|{date_start}||{sctr_salud}||\n'

            raw += template.format(
                type_identification_id=value['type_identification_id'],
                identification_id=value['identification_id'],
                cod_sunat_res_country=value['cod_sunat_res_country'],
                category_employee=value['category_employee'],
                date_start=value['date_start'],
                health_regime=value['health_regime'],
                eps_salud=value['eps_salud'],
                pension_system=value['pension_system'],
                worker_type_pensioner_provider=value['worker_type_pensioner_provider'],
                sctr_salud=value['sctr_salud'],
            )

        return raw.encode('utf8')

    def get_content_per_baja(self):
        raw = ''
        template = '{type_identification_id}|{identification_id}|{cod_sunat_res_country}|{category_employee}|1||' \
                   '{date_end}|{code}||\n'

        for value in self.per_data_baja:
            raw += template.format(
                type_identification_id=value['type_identification_id'],
                identification_id=value['identification_id'],
                cod_sunat_res_country=value['cod_sunat_res_country'],
                category_employee=value['category_employee'],
                date_end=value['date_end'],
                code=value['reason_low']

            )
        return raw.encode('utf8')

    def get_content_cta(self):
        raw = ''
        template = '{type_identification_id}|{identification_id}|{country_cod}|{cta_sueldo}|{nro_cta}\n'

        for value in self.cta_data:
            raw += template.format(
                type_identification_id=value['type_identification_id'],
                identification_id=value['identification_id'],
                country_cod=value['country_cod'],
                cta_sueldo=value['cta_sueldo'],
                nro_cta=value['nro_cta'],
            )
        return raw.encode('utf8')

    def get_content_edu(self):
        raw = ''
        template = '{type_identification_id}|{identification_id}|{cod_sunat_res_country}|{sit_edu}|{bool_edu}|{code_edu}|{code_career}|{edu_year}\n'

        for value in self.edu_data:
            raw += template.format(
                type_identification_id=value['type_identification_id'],
                identification_id=value['identification_id'],
                cod_sunat_res_country=value['cod_sunat_res_country'],
                sit_edu=value['sit_edu'],
                bool_edu=value['bool_edu'],
                code_edu=value['code_edu'],
                code_career=value['code_career'],
                edu_year=value['edu_year'],
            )
        return raw.encode('utf8')

    def get_content_est(self):
        raw = ''
        template = '{type_identification_id}|{identification_id}|{cod_sunat_res_country}|{cod_add}|{cod_anex}\n'

        for value in self.est_data:
            raw += template.format(
                type_identification_id=value['type_identification_id'],
                identification_id=value['identification_id'],
                cod_sunat_res_country=value['cod_sunat_res_country'],
                cod_add=value['cod_add'],
                cod_anex=value['cod_anex'],
        )
        return raw.encode('utf8')

    def get_content_lug(self):
        raw = ''
        template = '{type_identification_id}|{identification_id}|{cod_sunat_res_country}|{category_emp}|{cod_annex}\n'

        for value in self.lug_data:
            raw += template.format(
                type_identification_id=value['type_identification_id'],
                identification_id=value['identification_id'],
                cod_sunat_res_country=value['cod_sunat_res_country'],
                category_emp=value['category_emp'],
                cod_annex=value['cod_annex'],
            )
        return raw.encode('utf8')