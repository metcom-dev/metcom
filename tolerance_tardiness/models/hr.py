from datetime import datetime
from odoo import api, fields, models
from odoo.exceptions import ValidationError
import math
import pytz


class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    tardiness = fields.Char(
        string='Tardanza',
        readonly=True
    )

    @api.model
    def create(self, values):
        if values.get('check_in') and values.get('employee_id'):
            values['tardiness'] = self.calculate_tardiness(values['check_in'], values['employee_id'])
        return super(HrAttendance, self).create(values)

    def write(self, values):
        for rec in self:
            if values.get('check_in') and values.get('employee_id'):
                values['tardiness'] = self.calculate_tardiness(values['check_in'], values['employee_id'])
            elif values.get('check_in') and not values.get('employee_id'):
                values['tardiness'] = self.calculate_tardiness(values['check_in'], rec.employee_id.id)
            elif not values.get('check_in') and values.get('employee_id'):
                values['tardiness'] = self.calculate_tardiness(rec.check_in, values['employee_id'])
        return super(HrAttendance, self).write(values)

    @staticmethod
    def get_period_odd_even_week():
        # 1 == odd week    || 0 == even week
        today = fields.Date.today()
        week_type = '1' if int(math.floor((today.toordinal() - 1) / 7) % 2) else '0'
        return week_type

    def calculate_tardiness(self, check_in, employee_id):
        employee_id = self.env['hr.employee'].browse(employee_id)
        check_in = self.convert_date_timezone(check_in)
        schedule = employee_id.resource_calendar_id
        index = str(check_in.weekday())
        if schedule.two_weeks_calendar:
            week_type = self.get_period_odd_even_week()
            line_schedule = schedule.attendance_ids.filtered(
                lambda x: x.dayofweek == index and x.day_period == 'morning' and x.week_type == week_type and x.display_type != 'line_section')
        else:
            line_schedule = schedule.attendance_ids.filtered(lambda x: x.dayofweek == index and x.day_period == 'morning')
        if len(line_schedule) > 1:
            raise ValidationError('En la jornada laboral seteada en su ficha de empleado, '
                                  'tiene varios horarios que se traslapan en el mismo día({}),'
                                  ' primero debe corregirlo.'.format(index))
        elif len(line_schedule) == 0:
            raise ValidationError('En la jornada laboral seteada en su ficha de empleado, '
                                  'no tiene horario para el día de hoy.')

        hour_from = line_schedule.hour_from if line_schedule else False
        if check_in and hour_from:
            tolerance_min = employee_id.resource_calendar_id.tolerance_time
            if int(hour_from) > 1:
                min_to = (int(hour_from) * 60) + int((hour_from - int(hour_from)) * 100) + tolerance_min
            else:
                min_to = int((hour_from - int(hour_from)) * 100) + tolerance_min

            min_from = (int(check_in.hour) * 60) + int(check_in.minute)
            if min_from > min_to:
                total_min = min_from - min_to
                return self.get_hours_minutes(total_min)
        return False

    def convert_date_timezone(self, date_order, format_time='%Y-%m-%d %H:%M:%S'):
        tz = pytz.timezone(self.env.user.tz) if self.env.user.tz else pytz.utc
        if isinstance(date_order, str):
            date_order = datetime.strptime(date_order, format_time)
        if date_order:
            date_tz = pytz.utc.localize(date_order).astimezone(tz)
            date_order = date_tz.strftime(format_time)
            date_order = datetime.strptime(date_order, format_time)
        return date_order

    def get_hours_minutes(self, minutes):
        if minutes < 60:
            return '%d minuto(s)' % minutes
        else:
            hours = int(minutes / 60)
            mins = minutes - (hours * 60)
            return '%d hora(s) %d minuto(s)' % (hours, mins)


class ResourceCalendar(models.Model):
    _inherit = 'resource.calendar'

    tolerance_time = fields.Integer(
        string='Tiempo de tolerancia'
    )
