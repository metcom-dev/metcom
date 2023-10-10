from odoo import models, fields, api
from lxml import etree
from odoo.exceptions import UserError


class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'
    user_ids = fields.Many2many('res.users', string='Asignado a ')


class StockLocation(models.Model):
    _inherit = 'stock.location'

    user_ids_01 = fields.Many2many('res.users', string='Asignado a ')
    user_ids_02 = fields.Many2many('res.users', relation='responsable_', string='Responsable')

class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'
    users_warehouse_id = fields.Many2many('res.users', string='Asignado a ', related='warehouse_id.user_ids')

class StockPicking(models.Model):
    _inherit = 'stock.picking'
    user_logger = fields.Many2one('res.users', string='Asignado a ', default=lambda self: self.env.user, required=True, store=True)
    picking_type_id = fields.Many2one(
        'stock.picking.type', domain= "['|', ('warehouse_id.user_ids', 'in', user_logger), ('warehouse_id.user_ids', '=', False)]",
        required=True, check_company=True, index=True)

    location_id = fields.Many2one(
        'stock.location', 'Source Location',
        domain="['|', ('user_ids_01', 'in', user_logger), ('user_ids_01', '=', False)]",
        required=True)

    @api.depends('picking_type_id', 'partner_id')
    def _compute_location_id(self):
        for picking in self:
            picking = picking.with_company(picking.company_id)
            if picking.picking_type_id and picking.state == 'draft':
                if picking.picking_type_id.default_location_src_id :
                    location_id = picking.picking_type_id.default_location_src_id.id
                elif picking.partner_id:
                    location_id = picking.partner_id.property_stock_supplier.id
                else:
                    _customerloc, location_id = self.env['stock.warehouse']._get_partner_locations()

                if picking.picking_type_id.default_location_dest_id:
                    location_dest_id = picking.picking_type_id.default_location_dest_id.id
                elif picking.partner_id:
                    location_dest_id = picking.partner_id.property_stock_customer.id
                else:
                    location_dest_id, _supplierloc = self.env['stock.warehouse']._get_partner_locations()

                location = self.env['stock.location'].search([('id', '=', int(location_id))], limit=1)
                if picking.user_logger in location.user_ids_01  or not location.user_ids_01:
                    picking.location_id = location_id
                    picking.location_dest_id = location_dest_id


    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res_view = super(StockPicking, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        if view_type == 'form':
            user = self.env.user
            doc = etree.XML(res_view['arch'])
            value = "//field[@name='picking_type_id']"
            for node in doc.xpath(value):
                domain = "[ '|', ('warehouse_id.user_ids', 'in', {}), ('warehouse_id.user_ids', '=', False)]".format(user.id)
                domain = node.set("domain", domain)
            value = "//field[@name='location_id']"
            for node in doc.xpath(value):
                domain = "[ '|', ('user_ids_01', 'in', {}), ('user_ids_01', '=', False)]".format(user.id)
                domain = node.set("domain", domain)
            res_view['arch'] = etree.tostring(doc, encoding='unicode')

        return res_view

    def button_validate(self):
        message = "No puedes validar esta transacción, porque no eres el usuario responsable de " \
                  "la ubicación a la que estás enviando la Mercadería. Comunícate con el usuario responsable de " \
                  "la ubicación de Destino para que valide esta transacción."
        user = self.env.user

        if len(self.location_dest_id.user_ids_02) == 0:
            return super(StockPicking, self).button_validate()
        else:
            for i in range(len(self.location_dest_id.user_ids_02)):
                if self.location_dest_id.user_ids_02[i].id == user.id:
                    return super(StockPicking, self).button_validate()
        raise UserError(message)
