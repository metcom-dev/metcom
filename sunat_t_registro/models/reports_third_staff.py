class ThirdStaffRegistroReport(object):

    def __init__(self, med_data, ter_data, filename, obj):
        self.med_data = med_data
        self.ter_data = ter_data
        self.filename = filename
        self.obj = obj

    def get_filename(self, file_type):
        if file_type == 'med':
            filename = '{}.med'.format(self.filename)
        else:
            filename = '{}.ter'.format(self.filename)
        return filename

    def get_content_med(self):
        raw = ''
        template = '{ruc}|{type_service}|{date_from}|{date_to}\r\n'

        for value in self.med_data:
            raw += template.format(
                ruc=value['ruc'],
                type_service=value['type_service'],
                date_from=value['date_from'],
                date_to=value['date_to'],
            )
        return raw.encode('utf8')

    def get_content_ter(self):
        raw = ''
        template = '{l10n_pe_vat_code}|{identification_id}|{cod_pas_only}|{ruc}|{sctr}\r\n'

        for value in self.ter_data:
            raw += template.format(
                l10n_pe_vat_code=value['l10n_pe_vat_code'],
                identification_id=value['identification_id'],
                cod_pas_only=value['cod_pas_only'],
                ruc = value['ruc'],
                sctr = value['sctr'],
            )
        return raw.encode('utf8')
