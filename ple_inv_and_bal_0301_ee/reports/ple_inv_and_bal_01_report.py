class ReportInvBalTxt(object):

    def __init__(self, obj, data):
        self.obj = obj
        self.data = data
        self.indicator = None

    def get_content(self):
        raw = ''
        template = '{name}|{catalog_code}|{financial_state_code}|{credit}|{state}|\r\n'

        for value in self.data:
            raw += template.format(
                name=value['name'],
                catalog_code=value['catalog_code'],
                financial_state_code=value['financial_state_code'],
                credit=value['credit'],
                state=value['state'],
            )
        self.indicator = raw != ''
        return raw

    def get_filename(self):
        year, month, day = self.obj.date_end.strftime('%Y/%m/%d').split('/')
        return 'LE{vat}{period_year}{period_month}{period_day}030100{eeff_oportunity}{state_send}{has_info}11.txt'.format(
            vat=self.obj.company_id.vat,
            period_year=year,
            period_month=month,
            period_day=day,
            eeff_oportunity=self.obj.eeff_presentation_opportunity,
            state_send=self.obj.state_send or '',
            has_info='1' if self.indicator else '0'
        )
