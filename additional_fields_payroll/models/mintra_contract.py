from odoo import api, fields, models


class MintraContract(models.Model):

    _name = 'mintra.contract'
    _description = u'Tipo de Contrato - Mintra'

    code = fields.Char(
        string=u'Código'
    )
    mintra_description = fields.Char(
        string=u'Descripción'
    )

    def name_get(self):
        result = []
        for rec in self:
            result.append((rec.id, "[%s] %s" % (rec.code or '', rec.mintra_description or '')))
        return result
