class ReportInvBal20Txt(object):

    def __init__(self, obj, data):
        self.obj = obj
        self.data = data
        self.indicator = None

    def get_content(self):
        raw = ''
        template = '{period}|{code}|{code_rubro_estado_fin}|{balance_rubro_cont}|{indicador}|\r\n'

        for value in self.data:
            raw += template.format(
                period=value['period'],
                code=value['code'],
                code_rubro_estado_fin=value['code_rubro_estado_fin'],
                balance_rubro_cont=value['balance_rubro_cont'],
                indicador=value['indicador'],
            )

        self.indicator = raw != ''
        return raw

    def get_filename(self):

        return 'LE{ruc}{date}032000{code_opt_EEFF}{state_send}{indicator}11.txt'.format(
            ruc=self.obj.company_id.vat,
            date=self.obj.date_end.strftime('%Y%m%d'),
            code_opt_EEFF=self.obj.eeff_presentation_opportunity,
            state_send=self.obj.state_send,
            indicator='1' if self.indicator else '0',
        )