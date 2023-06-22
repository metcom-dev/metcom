from odoo import fields, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    firstname = fields.Char(
        string='Nombres',
        groups="hr.group_hr_user"
    )
    lastname = fields.Char(
        string='Apellido Paterno',
        groups="hr.group_hr_user"
    )
    secondname = fields.Char(
        string='Apellido Materno',
        groups="hr.group_hr_user"
    )

    relative_ids = fields.One2many(
        string="Parientes",
        comodel_name="hr.employee.relative",
        inverse_name="employee_id",
    )
