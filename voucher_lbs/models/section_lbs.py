from odoo import models, fields, api


class SectionLbs(models.Model):
    _name = 'section.lbs'
    _description = 'Sección de Liquidación'

    code = fields.Char(
        string='Código',
        size=1
    )
    description = fields.Char(
        string='Descripción'
    )

    def name_get(self):
        return [(obj.id, '[{}] {}'.format(obj.code, obj.description)) for obj in self]
