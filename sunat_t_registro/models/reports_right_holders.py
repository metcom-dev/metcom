from datetime import date


class ReportRightHolders(object):

    def __init__(self, obj, data, type):
        self.obj = obj
        self.data = data
        self.type = type

    def get_content_01(self):
        raw = ''
        template = '{type_identification_employee_code}|{identification_employee_num}|{type_identification_code}|{identification_num}|\
{code_pas_only}|{date_of_birth}|{first_lastname}|{second_lastname}|{name}|{gender}|{relation_type}|{doc_acreditation}|{n_doc_acred}|{month_pregnant}|\
{road_type_code}|{road_name}|{road_number}|{road_departament}|{road_inside}|{road_mz}|{road_batch}|{road_km}|\
{road_block}|{road_stage}|{zone_type_code}|{zone_name}|{zone_reference}|{zone_ubigeo_code}|\
{road_type_code_2}|{road_name_2}|{road_number_2}|{road_departament_2}|{road_inside_2}|{road_mz_2}|{road_batch_2}|{road_km_2}|\
{road_block_2}|{road_stage_2}|{zone_type_code_2}|{zone_name_2}|{zone_reference_2}|{zone_ubigeo_code_2}|\
{indicator_essalud}|{phone}|{email}|\
\r\n'

        for value in self.data:
            raw += template.format(
                type_identification_employee_code=value['type_identification_employee_code'],
                identification_employee_num=value['identification_employee_num'],
                type_identification_code=value['type_identification_code'],
                identification_num=value['identification_num'],
                code_pas_only=value['code_pas_only'],
                date_of_birth=value['date_of_birth'],
                first_lastname=value['first_lastname'],
                second_lastname=value['second_lastname'],
                name=value['name'],
                gender=value['gender'],
                relation_type=value['relation_type'],
                doc_acreditation=value['doc_acreditation'],
                n_doc_acred=value['n_doc_acred'],
                month_pregnant=value['month_pregnant'],

                road_type_code=value['road_type_code'],
                road_name=value['road_name'],
                road_number=value['road_number'],
                road_departament=value['road_departament'],
                road_inside=value['road_inside'],
                road_mz=value['road_mz'],
                road_batch=value['road_batch'],
                road_km=value['road_km'],
                road_block=value['road_block'],
                road_stage=value['road_stage'],
                zone_type_code=value['zone_type_code'],
                zone_name=value['zone_name'],
                zone_reference=value['zone_reference'],
                zone_ubigeo_code=value['zone_ubigeo_code'],

                road_type_code_2=value['road_type_code_2'],
                road_name_2=value['road_name_2'],
                road_number_2=value['road_number_2'],
                road_departament_2=value['road_departament_2'],
                road_inside_2=value['road_inside_2'],
                road_mz_2=value['road_mz_2'],
                road_batch_2=value['road_batch_2'],
                road_km_2=value['road_km_2'],
                road_block_2=value['road_block_2'],
                road_stage_2=value['road_stage_2'],
                zone_type_code_2=value['zone_type_code_2'],
                zone_name_2=value['zone_name_2'],
                zone_reference_2=value['zone_reference_2'],
                zone_ubigeo_code_2=value['zone_ubigeo_code_2'],

                indicator_essalud=value['indicator_essalud'],
                phone=value['phone'],
                email=value['email'],

            )
        return raw

    def get_content_02(self):
        raw = ''
        template = '{type_identification_employee_code}|{identification_employee_num}|{type_identification_code}|{identification_num}|\
{code_pas_only}|{date_of_birth}|{first_lastname}|{second_lastname}|{name}|{relation_type}|{low_date}|{reason_leave}|\r\n'

        for value in self.data:
            raw += template.format(
                type_identification_employee_code=value['type_identification_employee_code'],
                identification_employee_num=value['identification_employee_num'],
                type_identification_code=value['type_identification_code'],
                identification_num=value['identification_num'],
                code_pas_only=value['code_pas_only'],
                date_of_birth=value['date_of_birth'],
                first_lastname=value['first_lastname'],
                second_lastname=value['second_lastname'],
                name=value['name'],

                relation_type=value['relation_type'],
                low_date=value['low_date'],
                reason_leave=value['reason_leave'],
            )
        return raw

    def get_filename_01(self):
        return 'RD_{ruc}_{date}_ALTA.txt'.format(
            date=date.today().strftime('%Y%m%d'),
            ruc=self.obj.company_id.partner_id.vat,
            type=self.obj.type
        )

    def get_filename_02(self):

        return 'RD_{ruc}_{date}_BAJA.txt'.format(
            date=date.today().strftime('%Y%m%d'),
            ruc=self.obj.company_id.partner_id.vat,
        )

    def get_content(self):
        if self.type == 1: return self.get_content_01()
        elif self.type == 2: return self.get_content_02()
        else: return None

    def get_filename(self):
        if self.type == 1: return self.get_filename_01()
        elif self.type == 2: return self.get_filename_02()
        else: return None