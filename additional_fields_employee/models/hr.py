from odoo import models, fields, api


class HrContract(models.Model):
    _inherit = 'hr.contract'

    labor_regime_id = fields.Many2one(
        comodel_name="employee.regime",
        string='Régimen Laboral'
    )
    labor_condition_id = fields.Many2one(
        comodel_name='type.contract',
        string='Condición laboral'
    )
    maximum_working_day = fields.Boolean(
        string='Jornada de trabajo máxima'
    )
    atypical_cumulative_day = fields.Boolean(
        string='Jornada atípica o acumulativa'
    )
    nocturnal_schedule = fields.Boolean(
        string='Trabajo en horario nocturno'
    )
    unionized = fields.Boolean(
        string='Sindicalizado'
    )
    is_practitioner = fields.Boolean(
        string='¿Es practicante?'
    )
    work_occupation_id = fields.Many2one(
        comodel_name="work.occupation",
        string='Ocupación de trabajo'
    )


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    academic_degree_id = fields.Many2one(
        comodel_name='academic.degree',
        string='Situación Educativa',
        groups="hr.group_hr_user"
    )
    disability = fields.Boolean(
        string='Discapacidad',
        groups="hr.group_hr_user"
    )
    health_regime_id = fields.Many2one(
        comodel_name='health.regime',
        string='Régimen de Salud',
        groups="hr.group_hr_user"
    )
    fields_1_str = fields.Char(
        string='Campo 1',
        groups="hr.group_hr_user"
    )
    fields_2_str = fields.Char(
        string='Campo 2',
        groups="hr.group_hr_user"
    )
    fields_3_str = fields.Char(
        string='Campo 3',
        groups="hr.group_hr_user"
    )
    fields_4_str = fields.Char(
        string='Campo 4',
        groups="hr.group_hr_user"
    )
    fields_1_value = fields.Float(
        string='Campo 1 valor',
        groups="hr.group_hr_user"
    )
    fields_2_value = fields.Float(
        string='Campo 2 valor',
        groups="hr.group_hr_user"
    )
    fields_3_value = fields.Float(
        string='Campo 3 valor',
        groups="hr.group_hr_user"
    )
    fields_4_value = fields.Float(
        string='Campo 4 valor',
        groups="hr.group_hr_user"
    )
    fields_1_active = fields.Boolean(
        string='Campo 1 activo',
        groups="hr.group_hr_user"
    )
    fields_2_active = fields.Boolean(
        string='Campo 2 activo',
        groups="hr.group_hr_user"
    )
    fields_3_active = fields.Boolean(
        string='Campo 3 activo',
        groups="hr.group_hr_user"
    )
    fields_4_active = fields.Boolean(
        string='Campo 4 activo',
        groups="hr.group_hr_user"
    )
