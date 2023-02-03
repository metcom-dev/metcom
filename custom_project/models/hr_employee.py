from odoo import models, api

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        recs = self.search([('identification_id', operator, name)] + args, limit=limit)
        if not recs.ids:
            return super(HrEmployee, self).name_search(name=name, args=args,
                                                operator=operator,
                                                limit=limit)
        return recs.name_get()