from odoo import api, fields, models
from odoo.exceptions import ValidationError
import requests
import json


class ResCompany(models.Model):
    _inherit = 'res.company'

    url_provider_prod_intralot = fields.Char(string="Url Produccion")
    url_provider_test_intralot = fields.Char(string="Url Test")
    message_intralot = fields.Char(string="Mensaje")
    dni_intralot = fields.Char(string="DNI")
    password_intralot = fields.Char(string="Password")
    name_intralot = fields.Char(string="Nombre")
    primary_last_name_intralot = fields.Char(string="Apellido Paterno")
    second_last_name_intralot = fields.Char(string="Apellido Materno")
    position_intralot = fields.Char(string="Cargo")
    email_intralot = fields.Char(string="Email")


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    url_provider_prod_intralot = fields.Char(
        string="Url Produccion",
        related="company_id.url_provider_prod_intralot",
        readonly=False,
    )
    url_provider_test_intralot = fields.Char(
        string="Url Test",
        related="company_id.url_provider_test_intralot",
        readonly=False,
    )
    message_intralot = fields.Char(
        string="Mensaje",
        related="company_id.message_intralot",
        readonly=False,
    )
    dni_intralot = fields.Char(
        string="DNI",
        related="company_id.dni_intralot",
        readonly=False,
    )
    password_intralot = fields.Char(
        string="Password",
        related="company_id.password_intralot",
        readonly=False,
    )
    name_intralot = fields.Char(
        string="Nombre",
        related="company_id.name_intralot",
        readonly=False,
    )
    primary_last_name_intralot = fields.Char(
        string="Apellido Paterno",
        related="company_id.primary_last_name_intralot",
        readonly=False,
    )
    second_last_name_intralot = fields.Char(
        string="Apellido Materno",
        related="company_id.second_last_name_intralot",
        readonly=False,
    )
    position_intralot = fields.Char(
        string="Cargo",
        related="company_id.position_intralot",
        readonly=False,
    )
    email_intralot = fields.Char(
        string="Email",
        related="company_id.email_intralot",
        readonly=False,
    )

    def action_api_intralot(self):
        """Validate dni and password values whit api."""
        url = self.env.company.url_provider_prod_intralot
        dni = self.env.company.dni_intralot
        password = self.env.company.password_intralot
        data = {"dni": dni, "password": password}
        try:
            response = requests.post(url, data=json.dumps(data))
            response = response.content
            response = json.loads(response)
            if response.get("mensaje") == "OK":
                self.message_intralot = response.get("mensaje")
                self.name_intralot = response.get("nombre")
                self.primary_last_name_intralot = response.get("apellidopaterno")
                self.second_last_name_intralot = response.get("apellidomaterno")
                self.position_intralot = response.get("cargo")
                self.email_intralot = response.get("email")
                return response.get("token")
            else:
                raise ValidationError('Se intentó hacer la sincronizacion y el usuario o contrasena son invalidas. Debe añadir el URL en '
                                      'Inventario/Configuración/configuración Si no cuenta con ese acceso debe avisar a su administrador del sistema')

        except requests.exceptions.MissingSchema as error:
            raise ValidationError('Se intentó hacer la sincronizacion y el URL está vacío. Debe añadir el URL en Inventario/Configuración/configuración.'
                                  'Si no cuenta con ese acceso debe avisar a su administrador del sistema')