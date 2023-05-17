from odoo import models, fields, api


class LowReason(models.Model):

    _name = 'low.reason'
    _description = u'Motivo fin del periodo'

    code = fields.Char(
        string=u'Código'
    )
    low_reason_description = fields.Char(
        string=u'Descripción'
    )
    name = fields.Char(
        string=u'Abreviatura'
    )
