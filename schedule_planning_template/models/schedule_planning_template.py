# -*- coding: utf-8 -*-
import math
import pytz

from datetime import datetime, timedelta, time, date
from odoo import api, fields, models, _
from odoo.tools import format_time
# from odoo.addons.resource.models.resource import float_to_time
from odoo.exceptions import ValidationError

import logging
log = logging.getLogger(__name__)

class SchedulePlanningTemplate(models.Model):
    _name = 'schedule.planning.template'
    _description = "Schedule Template"
    _order = "sequence"

    name = fields.Char('Horas', compute="_compute_name")
    sequence = fields.Integer('Secuencia', index=True)
    start_time = fields.Float('Hora Inicial', default=0, group_operator=None, default_export_compatible=True)
    end_time = fields.Float('Hora Final', compute='_compute_name', group_operator=None)
    duration = fields.Float('Duración', default=0, group_operator=None, default_export_compatible=True)
    duration_days = fields.Integer('Duration Days', compute='_compute_name')

    _sql_constraints = [
        ('check_start_time_lower_than_24', 'CHECK(start_time < 24)', 'La hora inicial no puede ser mayor que 24.'),
        ('check_start_time_positive', 'CHECK(start_time >= 0)', 'La hora inicial no puede ser negativa.'),
        ('check_duration_positive', 'CHECK(duration >= 0)', 'La duración no puede ser negativa.')
    ]

    @api.constrains('duration')
    def _validate_duration(self):
        try:
            for schedule_template in self:
                datetime.today() + schedule_template._get_duration()
        except OverflowError:
            raise ValidationError(_("La duración seleccionada crea una fecha demasiado lejana en el futuro."))

    @api.depends('start_time', 'duration')
    def _compute_name(self):
        calendar = self.env.company.resource_calendar_id
        user_tz = pytz.timezone(self.env['planning.slot']._get_tz())
        today = date.today()
        for schedule_template in self:
            if not 0 <= schedule_template.start_time < 24:
                raise ValidationError(_('La hora inicial debe ser mayor o igual a 0 y menor que 24.'))
            start_time = time(hour=int(schedule_template.start_time), minute=round(math.modf(schedule_template.start_time)[0] / (1 / 60.0)))
            start_datetime = user_tz.localize(datetime.combine(today, start_time))
            schedule_template.duration_days, schedule_template.end_time = self._get_duration_days_end_time(start_datetime, schedule_template.duration)
            end_time = time(hour=int(schedule_template.end_time))
            schedule_template.name = '%s - %s %s' % (
                format_time(schedule_template.env, start_time, time_format='short').replace(':00 ', ' '),
                format_time(schedule_template.env, end_time, time_format='short').replace(':00 ', ' '),
                _('(lapso de %s días)') % (schedule_template.duration_days) if schedule_template.duration_days > 1 else ''
            )
        
    @api.model
    def _get_duration_days_end_time(self, start_datetime, duration):
        end_datetime = start_datetime + timedelta(hours=duration)
        if duration == 0 and start_datetime.hour == 0:
            end_datetime = end_datetime.replace(hour=0)

        return (
            math.ceil((end_datetime - start_datetime).total_seconds() / 3600 / 24),
            timedelta(hours=end_datetime.hour, minutes=end_datetime.minute).total_seconds() / 3600,
        )

    # @api.model
    # def _get_company_work_duration_data(self, calendar, start_datetime, duration):
    #     end_datetime = calendar.plan_hours(duration, start_datetime, compute_leaves=True)
    #     if duration == 0 and start_datetime.hour == 0:
    #         end_datetime = end_datetime.replace(hour=0)

    #     return (
    #         math.ceil(calendar.get_work_duration_data(start_datetime, end_datetime)['days']),
    #         timedelta(hours=end_datetime.hour, minutes=end_datetime.minute).total_seconds() / 3600,
    #     )

    def name_get(self):
        result = []
        for schedule_template in self:
            name = '%s' % (
                schedule_template.name
            )
            result.append([schedule_template.id, name])
        return result

    def _get_duration(self):
        self.ensure_one()
        return timedelta(hours=int(self.duration), minutes=round(math.modf(self.duration)[0] / (1 / 60.0)))