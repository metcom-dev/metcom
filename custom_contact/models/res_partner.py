from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    discharge_date = fields.Date(string='Fecha de alta')
    is_carrier = fields.Boolean(string='Es transportista')
    is_domiciled = fields.Boolean(string='Es domiciliado')
    is_worker = fields.Boolean(string='Es trabajador')
    is_seller = fields.Boolean(string='Es vendedor')
    is_collector = fields.Boolean(string='Es cobrador')
    is_driver = fields.Boolean(string='Es chofer')
    is_bank = fields.Boolean(string='Es banco')
    start_date = fields.Date(string='Fecha de inicio')
    end_date = fields.Date(string='Fecha de fin')