from odoo import models, fields, api


class HrLeave(models.Model):
    _inherit = 'hr.leave'

    utilities = fields.Boolean(
        string='¿Aplica para utilidades?',
        related='holiday_status_id.utilities'
    )


class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    utilities = fields.Boolean(
        string='¿Aplica para utilidades?',
        related='holiday_status_id.utilities'
    )


class HrPayslipWorkedDays(models.Model):
    _inherit = 'hr.payslip.worked_days'

    utilities = fields.Boolean(
        string='¿Aplica para utilidades?',
        related='work_entry_type_id.utilities'
    )
