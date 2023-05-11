from lxml import etree
from odoo import models, fields, api


class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(ResPartnerBank, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        if view_type == 'search':
            doc = etree.XML(res['arch'])
            for node in doc.xpath("//filter[@name='company_accounts']"):
                modifiers = "[('partner_id', '=', {})]"
                modifiers = modifiers.format(self.env.user.company_id.partner_id.id)
                node.set('domain', modifiers)
            res['arch'] = etree.tostring(doc, encoding='unicode')
        return res
