from odoo import api, fields, models


class HrPartnerConcept(models.Model):
    _name = "hr.partner.concept"
    _description = "Partner Concept"

    salary_rule = fields.Many2one(
        comodel_name='hr.salary.rule',
        string='Regla salarial'
    )
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Contacto',
        ondelete='restrict'
    )
    debit = fields.Boolean(string='Debito')
    credit = fields.Boolean(string='Crédito')
    amount = fields.Float(string='Importe')
    percentage = fields.Float(string='Porcentaje %')
    is_active = fields.Boolean(string='Activo')
    start_date = fields.Date(string='Fecha Inicio')
    end_date = fields.Date(string='Fecha Fin')


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    partner_concept_ids = fields.Many2many(
        comodel_name='hr.partner.concept',
        relation='hr_employee_hr_partner_concept_rel',
        string='Reglas Salariales',
        groups='hr.group_hr_user',
    )
