from odoo import models, fields


class TypeInputs(models.Model):
    _name = "type.inputs"
    _description = 'Tipos de Entrada de trabajo boletas'

    name = fields.Char('Nombre')
    code = fields.Char('Codigo')
    description = fields.Char('Descripcion')

    def name_get(self):
        res = []
        for record in self:
            res.append(record.name)
        return res
