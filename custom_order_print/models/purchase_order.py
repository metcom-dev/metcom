from odoo import fields, api, models, _

import logging
log = logging.getLogger(__name__)

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    carrier_id = fields.Many2one('res.partner', string='Transportista', domain=[('is_carrier', '=', True)])
    bank_type = fields.Many2one('res.bank', string='Banco')
    partner_banks = fields.One2many(related='partner_id.bank_ids', readonly=True)
    allowed_bank_type_ids = fields.Many2many(
        'res.bank', compute='_compute_allowed_bank_type_ids'
    )

    @api.depends('partner_id')
    def _compute_allowed_bank_type_ids(self):
        for order in self:
            bank_type_ids = []
            for bank in order.partner_id.bank_ids:
                if bank.bank_id.id not in bank_type_ids:
                    bank_type_ids.append(bank.bank_id.id)
            if not bank_type_ids:
                order.bank_type = False
            order.allowed_bank_type_ids = bank_type_ids

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.partner_id:
            self.bank_type = False
            bank_type_ids = []
            if self.partner_id.bank_ids: 
                for bank in self.partner_id.bank_ids:
                    if bank.bank_id.id not in bank_type_ids:
                        bank_type_ids.append(bank.bank_id.id)
                return {'domain': {'bank_type': [('id', 'in', bank_type_ids)]}}
            else:
                self.bank_type = False 
                return {'domain': {'bank_type': []}}
        else:
            self.bank_type = False
            return {'domain': {'bank_type': []}}
        
    