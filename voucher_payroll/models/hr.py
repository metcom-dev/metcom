from odoo import models, fields, api


class HrSalaryRuleCategory(models.Model):
    _inherit = 'hr.salary.rule.category'

    invoice_position = fields.Selection(
        string='Posición en Boleta',
        selection=[
            ("pos_1", "1"),
            ("pos_2", "2"),
            ("pos_3", "3")
        ],
        default="pos_1"
    )


class HrContract(models.Model):
    _inherit = 'hr.contract'

    hiden_overtime = fields.Boolean(string='No mostrar horas extras en boleta')
