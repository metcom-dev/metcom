from odoo import models, fields, api

import datetime

import logging
log = logging.getLogger(__name__)

class ManagementNotifications(models.Model):
    _name = 'management.notifications'
    _description = 'Notification Management'
    
    user_id = fields.Many2one('res.users', string='User')
    create_project = fields.Boolean(string='Creacion de Proyecto')
    new_requirement = fields.Boolean(string='Nuevo Requerimiento')
    purchase_order_created = fields.Boolean(string='Orden de Compra Creada')
    change_status_project = fields.Boolean(string='Cambio de Estado de Proyecto')
    change_stage_project = fields.Boolean(string='Cambio de Etapa de Proyecto')
    product_created = fields.Boolean(string='Producto Creado')
    contact_created = fields.Boolean(string='Contacto Creado')
    invoice_income = fields.Boolean(string='Factura de Ingreso')

    def get_mails(self, notification):
        notification_preferences = self.search([
            (notification, '=', True),
        ])
        emails_to_notify = [pref.user_id.email for pref in notification_preferences if pref.user_id.email]
        return emails_to_notify
    
    def send_notifications(self, notification, subject, body_html):
        emails_to_notify = self.get_mails(notification)
        log.info('emails_to_notify: %s', emails_to_notify)

        mail_body = """
        <body>
            <div style="margin: 0; padding: 0; font-family: Arial, sans-serif;">
                <div style="background-color: #0079c1; color: white; padding: 20px;">
                    <h2 style="margin: 0;">Notificación de {company_name}</h2>
                </div>
                <div style="padding: 20px;">
                    <h3 style="color: #0079c1;">Hola,</h3>
                    {content_body}
                    <p>Este es un mensaje automático, por favor no responda a este correo.</p>
                    <p>Saludos,</p>
                    <p>Equipo de {company_name}</p>
                </div>
                <div style="background-color: #f2f2f2; color: #606060; padding: 20px; text-align: center;">
                    <p>© {year} {company_name}. Todos los derechos reservados.</p>
                </div>
            </div>
        </body>
        """.format(content_body=body_html, year=datetime.datetime.now().year, company_name=self.env.company.name)

        if emails_to_notify:
            email_to = ','.join(emails_to_notify)
            log.info('email_to: %s', email_to)
            mail_id = self.env['mail.mail'].create({
                'subject': subject,
                'body_html': mail_body,
                'email_to': 'victor.huaycho@tecsup.edu.pe,vhuaycho@conflux.pe',
                'auto_delete': True,
                'message_type': 'email',
            })
            mail_id.send()
    
class Project(models.Model):
    _inherit = 'project.project'

    @api.model
    def create(self, vals):
        res = super(Project, self).create(vals)

        self.env['management.notifications'].send_notifications(
            notification='create_project', 
            subject='Nuevo Proyecto creado', 
            body_html='<p>Se ha creado un nuevo proyecto: {name} </p>'.format(name=res.name)
        )

        return res
    
    def write(self, vals):
        res = super(Project, self).write(vals)
        
        if 'stage_id' in vals:
            log.info('project.values: %s', vals)
            self.env['management.notifications'].send_notifications(
                notification='change_stage_project', 
                subject='Modificacion de Etapas de Proyecto', 
                body_html='<p>Se ha modificado la Etapa del proyecto: {name} </p>'.format(name=self.name) + '<p>Etapa: {stage} </p>'.format(stage=self.stage_id.name)
            )

        if 'last_update_id' in vals:
            log.info('project.values: %s', vals)
            self.env['management.notifications'].send_notifications(
                notification='change_status_project', 
                subject='Modificacion de Estado de Proyecto', 
                body_html='<p>Se ha modificado el Estado del proyecto: {name} </p>'.format(name=self.name) + '<p>Estado: {last_update_status} </p>'.format(last_update_status=self.last_update_id.name)
            )

        return res
    
class PurchasePreOrder(models.Model):
    _inherit = 'purchase.preorder'

    @api.model
    def create(self, vals):
        res = super(PurchasePreOrder, self).create(vals)

        self.env['management.notifications'].send_notifications(
            notification='new_requirement', 
            subject='Nuevo requerimiento creado', 
            body_html='<p>Se ha creado un nuevo requerimiento: {name} </p>'.format(name=res.name) + '<p>Proyecto: {project_id} </p>'.format(project_id=res.project_id.name)
        )

        return res
    
class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.model
    def create(self, vals):
        res = super(PurchaseOrder, self).create(vals)

        self.env['management.notifications'].send_notifications(
            notification='purchase_order_created', 
            subject='Nueva Orden de Compra Creada', 
            body_html='<p>Se ha creado una nueva Orden de Compra: {name} </p>'.format(name=res.name) + '<p>De Preorden: {preorder_id} </p>'.format(preorder_id=res.from_preorders)
        )

        return res
    
class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.model
    def create(self, vals):
        res = super(ProductProduct, self).create(vals)

        self.env['management.notifications'].send_notifications(
            notification='product_created', 
            subject='Nuevo Producto Creado', 
            body_html='<p>Se ha creado un nuevo producto: {name}</p>'.format(name=res.name)
        )

        return res
    
class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def create(self, vals):
        res = super(ResPartner, self).create(vals)

        self.env['management.notifications'].send_notifications(
            notification='contact_created', 
            subject='Nuevo Contacto Creado', 
            body_html='<p>Se ha creado un nuevo contacto: {name}</p>'.format(name=res.name)
        )

        return res
    
class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_post(self):
        res = super(AccountMove, self).action_post()

        self.env['management.notifications'].send_notifications(
            notification='invoice_income', 
            subject='Nueva Factura de Publicada', 
            body_html='<p>Se ha publicado una factura: {name}</p>'.format(name=self.name)
        )

        return res



    