from odoo import api, fields, models


class HrWorkEntryType(models.Model):
    _inherit = 'hr.work.entry.type'

    utilities = fields.Boolean(string='¿Aplica para utilidades?')


class HrLeaveType(models.Model):
    _inherit = 'hr.leave.type'

    utilities = fields.Boolean(
        string='¿Aplica para utilidades?',
        related='work_entry_type_id.utilities'
    )


class HrSalaryRule(models.Model):
    _inherit = 'hr.salary.rule'

    utilities = fields.Boolean(string='¿Aplica para utilidades?')


class HrPayslipLine(models.Model):
    _inherit = 'hr.payslip.line'

    utilities = fields.Boolean(
        string='¿Aplica para utilidades?',
        related='salary_rule_id.utilities'
    )
