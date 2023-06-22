from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
from odoo.addons.resource.models.resource import HOURS_PER_DAY


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    def action_validate_extra_hours(self):
        holiday_status_id = self.env.ref('automatic_leave_type.hr_leave_type_27', False)
        for rec in self:
            if not rec.is_validate_extra_hour and rec.employee_id and holiday_status_id and rec.hours_compensate:
                rec.is_validate_extra_hour = True
                date_review = fields.Date.today() - relativedelta(days=1)
                value = 0
                if rec.hours_compensate and not rec.extra_hours_morning and not rec.extra_hours:
                    value += rec.unit_amount
                if rec.extra_hours_morning or rec.extra_hours:
                    value += rec.hours_compensate
                allocation_model = self.env['hr.leave.allocation']
                allocation_id = allocation_model.search([
                    ('employee_id', '=', rec.employee_id.id),
                    ('from_date', '=', date_review),
                    ('to_date', '=', date_review),
                    ('holiday_type', '=', 'employee'),
                    ('holiday_status_id', '=', holiday_status_id.id),
                ], limit=1)
                if not allocation_id:
                    allocation_id = self.env['hr.leave.allocation'].create({
                        'name': u'Días/Horas compensadas',
                        'holiday_type': 'employee',
                        'employee_id': rec.employee_id.id,
                        'from_date': date_review,
                        'to_date': date_review,
                        'holiday_status_id': holiday_status_id.id,
                    })
                allocation_id.number_of_days += (value / HOURS_PER_DAY)
        super(AccountAnalyticLine, self).action_validate_extra_hours()
