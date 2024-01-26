from odoo import models, fields, api
from odoo.osv import expression


class ProductionLotStatus(models.Model):
    _name = 'stock.production.lot.status'
    _description = 'Status Stock Production Lot'

    code = fields.Char(string='Code')
    name = fields.Char(string='name')

    def name_get(self):
        res = []
        for _ in self:
            name = "%s-%s" % (_.code, _.name)
            res.append((_.id, name))
        return res

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('code', '=ilike', name.split(' ')[0] + '%'), ('name', operator, name)]
            if operator in expression.NEGATIVE_TERM_OPERATORS:
                domain = ['&', '!'] + domain[1:]
        return self._search(expression.AND([domain, args]), limit=limit, access_rights_uid=name_get_uid)
