from odoo import api, models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def get_structured_address(self):
        self.ensure_one()
        address = "{}, {}, {}, {}, {}".format(
            self.street or '', self.l10n_pe_district.name or '', self.city_id.name or '', self.state_id.name or '', self.country_id.name or '')
        return address