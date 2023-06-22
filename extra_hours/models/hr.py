from datetime import datetime
from odoo import api, fields, models
import math
import pytz


class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    dayofweek = fields.Selection(
        selection=[
            ('0', 'Lunes'),
            ('1', 'Martes'),
            ('2', 'Miércoles'),
            ('3', 'Jueves'),
            ('4', 'Viernes'),
            ('5', 'Sábado'),
            ('6', 'Domingo')
        ],
        string='Día de la semana',
        compute='_compute_dayofweek',
        store=True
    )
    extra_hours = fields.Float(
        string='Horas Extras',
        readonly=True,
        help='Compara la jornada del trabajador “entrada y salida” con el campo minutos permitidos para horas extras '
             'ubicado en configuración y si tiene una diferencia positiva que se puede considerar como horas extras '
             'trae la información.'
    )
    hours_part = fields.Float(
        string='Parte de Horas',
        compute='compute_hours_part',
        store=True,
        help='Filtra al trabajador y el día en partes de horas y si tiene Horas extras registradas las trae.'
    )
    extra_hours_ids = fields.One2many(
        comodel_name='account.analytic.line',
        inverse_name='attendance_id',
        string='Detalle de Horas extra'
    )
    difference = fields.Boolean(
        string='Diferencia No permitida',
        compute='_compute_difference',
        store=True
    )

    @api.depends('extra_hours', 'hours_part')
    def _compute_difference(self):
        for rec in self:
            val = abs(rec.extra_hours - rec.hours_part)
            diff_extra_part_min = float(
                self.env['ir.config_parameter'].sudo().get_param('extra_hours.diff_extra_part_min'))
            if val > diff_extra_part_min:
                rec.difference = True
            else:
                rec.difference = False

    @api.depends('check_in')
    def _compute_dayofweek(self):
        for rec in self:
            if rec.check_in:
                rec.dayofweek = str(rec.check_in.weekday())
            else:
                rec.dayofweek = False

    @staticmethod
    def get_period_odd_even_week():
        # 1 == odd week    || 0 == even week
        today = fields.Date.today()
        week_type = '1' if int(math.floor((today.toordinal() - 1) / 7) % 2) else '0'
        return week_type

    def action_calc_extra_hours(self):
        for rec in self:
            dayofweek = rec.dayofweek
            if not dayofweek:
                continue

            schedule = rec.employee_id.resource_calendar_id
            if schedule.two_weeks_calendar:
                week_type = self.get_period_odd_even_week()
                today = sorted(schedule.attendance_ids.filtered(
                    lambda x: x.dayofweek == dayofweek and x.day_period == 'morning' and
                    x.week_type == week_type and x.display_type != 'line_section'), key=lambda x: x.hour_from)
            else:
                today = sorted(schedule.attendance_ids.filtered(
                    lambda x: x.dayofweek == dayofweek and x.day_period == 'morning'), key=lambda x: x.hour_from)

            if not today:
                continue
            min_minutes_extra_hours = float(self.env['ir.config_parameter'].sudo().get_param(
                'extra_hours.min_minutes_extra_hours'))
            extra = 0
            check_in = self._convert_date_timezone(rec.check_in)
            check_in_min = self._convert_datetime_to_time(check_in)
            hour_from = today[0].hour_from
            value = abs(hour_from - check_in_min)
            if check_in_min < hour_from and value >= min_minutes_extra_hours:
                extra += value
            length_day = len(today)
            hour_to = today[length_day - 1].hour_to
            check_out = self._convert_date_timezone(rec.check_out)
            check_out_min = self._convert_datetime_to_time(check_out)
            value = abs(check_out_min - hour_to)
            if check_out_min > hour_to and value >= min_minutes_extra_hours:
                extra += value
            rec.extra_hours = extra

    @staticmethod
    def _convert_datetime_to_time(value):
        val = value.hour + (value.minute / 60)
        return val

    def _convert_date_timezone(self, date_order, format_time='%Y-%m-%d %H:%M:%S'):
        tz = pytz.timezone(self.env.user.tz) if self.env.user.tz else pytz.utc
        if isinstance(date_order, str):
            date_order = datetime.strptime(date_order, format_time)
        if date_order:
            date_tz = pytz.utc.localize(date_order).astimezone(tz)
            date_order = date_tz.strftime(format_time)
            date_order = datetime.strptime(date_order, format_time)
        return date_order

    def action_get_extra_hours_lines(self):
        for rec in self:
            if rec.extra_hours_ids:
                rec.extra_hours_ids.write({'attendance_id': False})
            analytic_lines_ids = self.env['account.analytic.line'].search([
                ('employee_id', '=', rec.employee_id.id),
                ('extra_hours', '=', True),
                ('date', '=', rec.check_in.date())
            ])
            if analytic_lines_ids:
                analytic_lines_ids.write({'attendance_id': rec.id})

    @api.depends('extra_hours_ids', 'extra_hours_ids.unit_amount')
    def compute_hours_part(self):
        for rec in self:
            rec.hours_part = sum(line.unit_amount for line in rec.extra_hours_ids)
