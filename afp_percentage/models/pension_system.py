from bs4 import BeautifulSoup
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api
import logging
import urllib.request
import urllib.parse
from datetime import datetime

_logger = logging.getLogger(__name__)
now = datetime.now()


class PensionSystem(models.Model):
    _inherit = 'pension.system'

    @api.model
    def afp_method(self):
        try:
            self.button_afp_method()
        except urllib.error.HTTPError as http_error:
            _logger.warning('Error: {}'.format(http_error))
        except urllib.error.URLError as url_error:
            _logger.warning('Error: {}'.format(url_error))
        except Exception as exception_error:
            _logger.warning('Error: {}'.format(exception_error))

    def button_afp_method(self):
        
        url = 'https://www.sbs.gob.pe/app/spp/empleadores/comisiones_spp/paginas/comision_prima.aspx'
        afp_data = []
        percentage = 100
        open_html = urllib.request.urlopen(url)
        html = BeautifulSoup(open_html, "lxml")
        tr_array = html.findAll("tr", {"class": "JER_filaContenido"})
        for td in tr_array:
            rows = td.findAll('td')
            for row in rows:
                str_temp = str(row.text.strip())
                str_temp = str_temp.replace('%', '').replace(',', '')
                afp_data.append(str_temp)
        
        habitat = self.env.ref('types_system_pension.pension_system_25')
        integra = self.env.ref('types_system_pension.pension_system_21')
        profuturo = self.env.ref('types_system_pension.pension_system_23')
        prima = self.env.ref('types_system_pension.pension_system_24')

        init_date = datetime(now.year, now.month, 1).date()
        last_day = datetime.now() + relativedelta(day=1, months=+1, days=-1)

        pension_line_habitat = {
            'date_from': init_date,
            'date_to': last_day,
            'fund': float(afp_data[4]) / percentage,  
            'bonus': float(afp_data[3]) / percentage,  
            'mixed_flow': 0.0, 
            'flow': float(afp_data[1]) / percentage, 
            'balance': float(afp_data[2]) / percentage,  
        }

        pension_line_integra = {
            'date_from': init_date,
            'date_to': last_day,
            'fund': float(afp_data[10]) / percentage,  
            'bonus': float(afp_data[9]) / percentage, 
            'mixed_flow': 0.0, 
            'flow': float(afp_data[7]) / percentage, 
            'balance': float(afp_data[8]) / percentage, 
        }

        pension_line_prima = {
            'date_from': init_date,
            'date_to': last_day,
            'fund': float(afp_data[16]) / percentage,  
            'bonus': float(afp_data[15]) / percentage,  
            'mixed_flow': 0.0, 
            'flow': float(afp_data[13]) / percentage, 
            'balance': float(afp_data[14]) / percentage,  
        }

        pension_line_profuturo = {
            'date_from': init_date,
            'date_to': last_day,
            'fund': float(afp_data[22]) / percentage,  
            'bonus': float(afp_data[21]) / percentage,  
            'mixed_flow': 0.0,  
            'flow': float(afp_data[19]) / percentage,  
            'balance': float(afp_data[20]) / percentage,  
        }


        if not self.env['tope.afp'].search([("date_from", "=", init_date)]):
            self.env['tope.afp'].create({
                'date_from': init_date,
                'date_to': last_day,
                'top': float(afp_data[5].replace(' ', '')),
            })

        flag = False
        for i in habitat.comis_pension_ids:
            if i.date_from == init_date:
                flag = True
        if not flag:
            habitat.comis_pension_ids = [(0, 0, pension_line_habitat)]

        flag = False
        for i in integra.comis_pension_ids:
            if i.date_from == init_date:
                flag = True
        if not flag:
            integra.comis_pension_ids = [(0, 0, pension_line_integra)]

        flag = False
        for i in profuturo.comis_pension_ids:
            if i.date_from == init_date:
                flag = True
        if not flag:
            profuturo.comis_pension_ids = [(0, 0, pension_line_profuturo)]

        flag = False
        for i in prima.comis_pension_ids:

            if i.date_from == init_date:
                flag = True
        if not flag:
            prima.comis_pension_ids = [(0, 0, pension_line_prima)]