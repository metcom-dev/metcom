# -*- coding: utf-8 -*-
from werkzeug.urls import url_encode

from odoo import models, api, fields, _
from odoo.exceptions import UserError, ValidationError


class PrePurchase(models.Model):
	_name = 'purchase.preorder'
	_inherit = ['mail.thread', 'mail.activity.mixin']
	_description = 'Pre-orden de Compra'
	_order = 'date_order desc'

	name = fields.Char(
		string='Referencia',
		default='/',
		copy=False,
	)
	state = fields.Selection(
		string='Estado',
		selection=[
			('draft', 'Borrador'), 
			('open', 'Abierto'),
			('preorder', 'Validado'),
			('cancel', 'Cancelado'),
		],
		default='draft',
	)
	priority = fields.Selection(
		string='Urgencia',
		selection=[
			('high', 'Alto'), 
			('medium', 'Medio'),
			('low', 'Bajo'),
		],
		default='medium',
		required=True,
	)
	user_id = fields.Many2one(
		string='Usuario',
		comodel_name='res.users',
		default=lambda self: self.env.user,
		required=True,
	)
	validate_user_id = fields.Many2one(
		string='Usuario Validador',
		comodel_name='res.users',
	)
	location_id = fields.Many2one(
		string='Ubicación de Almacén',
		comodel_name='stock.location',
		ondelete='restrict',
	)
	company_id = fields.Many2one(
		string='Compañía',
		comodel_name='res.company',
		default=lambda self: self.env.user.company_id,
		ondelete='restrict',
	)
	date_order = fields.Datetime(
		string='Fecha de Pedido',
		default=fields.Datetime.now,
	)
	date_validate = fields.Datetime(
		string='Fecha de Validación',
		copy=False,
	)
	line_ids = fields.One2many(
		string='Lineas',
		comodel_name='purchase.preorder.line',
		inverse_name='preorder_id',
		copy=True,
	)
	note = fields.Text(
		string='Obervaciones',
	)
	check_stock = fields.Boolean(
		string='Se revisó el stock',
		default=False,
		copy=False,
	)

	def get_quantity_stock(self):
		for rec in self:
			if not rec.location_id:
				raise UserError("Defina una ubicación de inventario")
			for line in rec.line_ids:
				quant_id = self.env['stock.quant'].search([('product_id', '=', line.product_id.id), ('location_id', '=', rec.location_id.id)], limit=1)
				line.stock_qty = quant_id.quantity if quant_id else 0
				line.product_stock_uom = quant_id.product_uom_id if quant_id else line.product_stock_uom
				line.stock_date = fields.Datetime.now(rec)
				line._onchange_stock_qty()
			rec.check_stock = True
			rec.message_post(body="Se revisó el stock")

	def create_purchase_order(self):
		Purchase = self.env['purchase.order']
		po_ids = []
		for rec in self:
			po_lines = []
			for line in rec.line_ids:
				if line.product_qty > 0 and line.state == 'done':
					po_lines.append([0, 0, {
						'name': line.product_id.display_name,
						'product_id': line.product_id.id,
						'product_qty': line.purchase_product_qty,
						'product_uom': line.purchase_product_uom.id,
						'date_planned': fields.Date.context_today(self),
						'price_unit': 0,
                        'taxes_id': [(6, 0, line.product_id.supplier_taxes_id.ids)],
					}])
			if len(po_lines) == 0:
				continue
			po_id = Purchase.create({
				'partner_id': self.env.user.company_id.partner_id.id,
				'order_line': po_lines
			})
			rec.message_post(body="Se creo la orden de compra <a href='#' data-oe-model='purchase.order' data-oe-id='%s'>%s</a>" % (po_id.id, po_id.name))
			po_id.message_post(body="Creado desde <a href='#' data-oe-model='purchase.preorder' data-oe-id='%s'>%s</a>" % (rec.id, rec.name))
			if len(self) == 1:
				return {
					'name': "Orden de compra",
					'view_mode': 'form',
					'view_type': 'form',
					'view_id': self.env.ref('purchase.purchase_order_form').id,
					'res_model': 'purchase.order',
					'res_id': po_id.id,
					'type': 'ir.actions.act_window',
					'nodestroy': True,
					'target': 'current',
					'domain': ""
				}
			else:
				po_ids.append(po_id.id)
		if len(po_ids) == 0:
			raise UserError("No se creo la compra, verifique que tenga lineas validadas")
		print("return tree", po_ids)

	def send_validate(self):
		for rec in self:
			if not rec.validate_user_id:
				raise UserError("Defina un usuario para validar")
			if rec.name == '/':
				sequence = self.env['ir.sequence'].next_by_code('purchase_preorder.purchase_preorder_sequence')
				rec.name = sequence
			rec.state = 'open'
			for line in rec.line_ids:
				line.action_open()

	def action_draft(self):
		for rec in self:
			for line in rec.line_ids:
				line.action_open()
			rec.date_validate = False
			rec.state = 'draft'

	def action_validate(self):
		for rec in self:
			lines_done = [line for line in rec.line_ids if line.state == 'done']
			if len(lines_done) == 0:
				raise UserError("Debe validar al menos una linea para continuar")
			rec.date_validate = fields.Datetime.now(self)
			rec.state = 'preorder'

	def action_send_lines_done(self):
		for rec in self:
			for line in rec.line_ids:
				line.action_done()

	def action_cancel(self):
		for rec in self:
			for line in rec.line_ids:
				line.action_cancel()
			rec.state = 'cancel'

	def action_preorder_send(self):
		self.ensure_one()
		ir_model_data = self.env['ir.model.data']
		try:
			template_id = ir_model_data._xmlid_lookup('purchase_preorder.email_template_preorder')[2]
		except ValueError:
			template_id = False
		try:
			compose_form_id = ir_model_data._xmlid_lookup('mail.email_compose_message_wizard_form')[2]
		except ValueError:
			compose_form_id = False
		ctx = {
			'default_model': 'purchase.preorder',
            'active_model': 'purchase.preorder',
			'active_id': self.ids[0],
			'default_res_id': self.ids[0],
			'default_use_template': bool(template_id),
			'default_template_id': template_id,
			'default_composition_mode': 'comment',
			'default_email_layout_xmlid': "mail.mail_notification_layout_with_responsible_signature",
			'mark_so_as_sent': True,
			'force_email': True
		}
		return {
			'name': _('Compose Email'),
			'type': 'ir.actions.act_window',
			'view_mode': 'form',
			'res_model': 'mail.compose.message',
			'views': [(compose_form_id, 'form')],
			'view_id': compose_form_id,
			'target': 'new',
			'context': ctx,
		}

	def get_mail_url(self):
		self.ensure_one()
		params = {
			'model': self._name,
			'res_id': self.id,
		}
		params = {
			'view_type': 'form',
			'model': 'purchase.preorder',
			'id': self.id,
		}
		return '/web#' + url_encode(params)

	def print_preorder(self):
		return self.env.ref('purchase_preorder.report_purchase_preorder').report_action(self)


class PrePurchaseLine(models.Model):
	_name = 'purchase.preorder.line'
	_description = 'Linea Pre-orden de Compra'

	preorder_id = fields.Many2one(
		string='Pre-orden',
		comodel_name='purchase.preorder',
		ondelete='cascade',
	)
	state = fields.Selection(
		string='Estado',
		selection=[
			('open', 'Abierto'),
			('done', 'Validado'),
			('cancel', 'Cancelado'),
		],
		default='open',
	)

	product_id = fields.Many2one(
		string='Producto',
		comodel_name='product.product',
		ondelete='restrict',
		required=True,
	)
	
	product_qty = fields.Float(
		string='Cantidad requerida',
	)
	product_uom = fields.Many2one(
		string='UdM',
		comodel_name='uom.uom',
		required=True,
	)

	stock_qty = fields.Float(
		string='Cantidad en stock',
	)
	product_stock_uom = fields.Many2one(
		string='UdM',
		comodel_name='uom.uom',
		required=True,
	)
	stock_date = fields.Datetime(
		string='Fecha de stock',
		default=fields.Datetime.now,
	)

	purchase_product_qty = fields.Float(
		string='Cantidad a comprar',
	)
	purchase_product_uom = fields.Many2one(
		string='UdM',
		comodel_name='uom.uom',
		required=True,
	)

	validate_user_id = fields.Many2one(
		string='Validado por',
		comodel_name='res.users',
	)

	@api.onchange('product_id')
	def _onchange_product_id(self):
		if not self.product_id:
			return
		self.product_stock_uom = self.product_id.uom_id.id
		self.product_uom = self.product_id.uom_po_id.id
		self.purchase_product_uom = self.product_id.uom_po_id.id

	@api.onchange('stock_qty')
	def _onchange_stock_qty(self):
		if self.product_stock_uom.id == self.product_uom.id:
			self.purchase_product_qty = self.product_qty - self.stock_qty if self.product_qty - self.stock_qty >= 0 else 0
			self.purchase_product_uom = self.product_stock_uom
		else:
			self.purchase_product_qty = 0
			self.purchase_product_uom = self.product_id.uom_id

	def action_open(self):
		for rec in self:
			rec.state = 'open'

	def action_done(self):
		for rec in self:
			rec.validate_user_id = self.env.user
			rec.state = 'done'

	def action_cancel(self):
		for rec in self:
			rec.state = 'cancel'