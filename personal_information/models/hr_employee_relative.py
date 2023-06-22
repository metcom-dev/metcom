from datetime import datetime

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models


class HrEmployeeRelative(models.Model):
    _name = "hr.employee.relative"
    _description = "HR Employee Relative"

    employee_id = fields.Many2one(string="Empleado", comodel_name="hr.employee")
    relation_id = fields.Many2one(
        "hr.employee.relative.relation", string="Parentesco", required=True
    )
    name = fields.Char(string="Nombre", required=True)
    partner_id = fields.Many2one(
        "res.partner",
        string="Contacto",
        domain=["&", ("is_company", "=", False), ("type", "=", "contact")],
    )
    gender = fields.Selection(
        string="Género",
        selection=[("masculino", "Masculino"), ("femenino", "Femenino"), ("otro", "Otro")],
    )
    date_of_birth = fields.Date(string="Fecha de Cumpleaños")
    age = fields.Float(string='Edad', compute="_compute_age")

    job = fields.Char(string='Profesión')
    phone_number = fields.Char(string='Teléfono')

    notes = fields.Text(string="Notas")

    @api.depends("date_of_birth")
    def _compute_age(self):
        for record in self:
            age = relativedelta(datetime.now(), record.date_of_birth)
            record.age = age.years + (age.months / 12)

    @api.onchange("partner_id")
    def _onchange_partner_id(self):
        if self.partner_id:
            self.name = self.partner_id.display_name
