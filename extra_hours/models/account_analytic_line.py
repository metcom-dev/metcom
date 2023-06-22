from odoo import api, fields, models


def _convert_time_to_float(value):
    if isinstance(value, str):
        value = float(value)
    int_val = int(value)
    value = value - int_val
    new_val = (value * 60) / 100
    new_val = int_val + new_val
    new_val = float('%.2f' % new_val)
    return new_val


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    name = fields.Char(required=False)
    extra_hours = fields.Boolean(
        string='H. E.',
        help='Horas Extras'
    )
    hours_compensate = fields.Boolean(
        string='H. C.',
        help='Horas a compensar'
    )
    extra_hours_morning = fields.Boolean(
        string='H. A.',
        help='Horas extras amanecida'
    )
    extra_hour_25 = fields.Float(
        string='H. E. 25%',
        compute='_compute_fields',
        store=True
    )
    extra_hour_35 = fields.Float(
        string='H. E. 35%',
        compute='_compute_fields',
        store=True
    )
    r_extra_hour_25 = fields.Float(
        string='R. H. E. 25%',
        compute='_compute_fields',
        store=True
    )
    r_extra_hour_35 = fields.Float(
        string='R. H. E. 35%',
        compute='_compute_fields',
        store=True
    )
    hour_100 = fields.Float(string='Horas 100%')
    r_hours_compensate = fields.Float(string='Horas compensadas')
    night_hours = fields.Float(
        string='Horas nocturnas',
        compute='_compute_fields',
        store=True
    )
    pay_date = fields.Date(string='Fecha de pago')
    attendance_id = fields.Many2one(
        comodel_name='hr.attendance',
        string='Asistencia'
    )
    error_dialog = fields.Text(
        string='Error',
        compute="_compute_error_dialog",
        store=True,
    )
    is_validate_extra_hour = fields.Boolean(string='Validar Hora Extra')

    @api.depends('extra_hour_35', 'r_extra_hour_35', 'extra_hour_25', 'extra_hour_35', 'extra_hours',
                 'extra_hours_morning', 'hours_compensate')
    def _compute_error_dialog(self):
        for rec in self:
            nro = 0
            msg = ''
            if rec.extra_hour_25 < 0:
                msg += 'El campo H.E 25% no puede ser negativo. Por {} horas.\n'.format(rec.extra_hour_25)
            if rec.extra_hour_35 < 0:
                nro += abs(rec.extra_hour_35)
                msg += 'El campo H.E 25% no puede ser negativo. Por {} horas.\n'.format(rec.extra_hour_35)
            if rec.r_extra_hour_35 < 0:
                nro += abs(rec.r_extra_hour_35)
                msg += 'El campo R.H.E 35% no puede ser negativo. Por {} horas.\n'.format(rec.r_extra_hour_35)
            if rec.r_extra_hour_25 < 0:
                msg += 'El campo R.H.E 25% no puede ser negativo. Por {} horas.\n'.format(rec.r_extra_hour_25)
            if nro > 0:
                nro = str(nro)
                if rec.hours_compensate:
                    msg += 'Horas compensadas supera a horas extras por {} horas.\n'.format(nro)
                rec.error_dialog = msg
            else:
                rec.error_dialog = False

    @api.depends('unit_amount', 'extra_hours', 'extra_hours_morning', 'r_hours_compensate', 'hour_100')
    def _compute_fields(self):
        for rec in self:
            rec.extra_hour_25 = rec.extra_hour_35 = rec.r_extra_hour_25 = rec.r_extra_hour_35 = 0
            if rec.extra_hours_morning:
                rec.night_hours = 7
            else:
                rec.night_hours = 0
            if rec.unit_amount and rec.unit_amount > 0:
                unit_amount = rec.unit_amount
                hour_100 = rec.hour_100
                if rec.extra_hours and not rec.extra_hours_morning:
                    if unit_amount > 2:
                        rec.extra_hour_25 = 2
                        rec.extra_hour_35 = unit_amount - 2
                    else:
                        rec.extra_hour_25 = rec.unit_amount
                        rec.extra_hour_35 = 0
                    if hour_100 > 0:
                        if rec.extra_hour_25 >= 2 and hour_100 >= 2:
                            rec.extra_hour_25 -= 2
                            hour_100 -= 2
                        if rec.extra_hour_25 >= 2 and hour_100 < 2:
                            rec.extra_hour_25 -= hour_100
                            hour_100 = 0
                        if rec.extra_hour_25 < 2 and hour_100 >= 2:
                            hour_100 -= rec.extra_hour_25
                            rec.extra_hour_25 = 0
                        if rec.extra_hour_25 < 2 and hour_100 < 2:
                            if rec.extra_hour_25 > hour_100:
                                rec.extra_hour_25 -= hour_100
                                hour_100 = 0
                            else:
                                hour_100 -= rec.extra_hour_25
                                rec.extra_hour_25 = 0
                        rec.extra_hour_35 = rec.extra_hour_35 - hour_100 if hour_100 <= rec.extra_hour_35 else 0

                elif rec.extra_hours and rec.extra_hours_morning:
                    if unit_amount > 2:
                        rec.r_extra_hour_25 = 2
                        rec.r_extra_hour_35 = unit_amount - 2
                    else:
                        rec.r_extra_hour_25 = rec.unit_amount
                        rec.r_extra_hour_35 = 0

                    if hour_100 > 0:
                        if rec.r_extra_hour_25 >= 2 and hour_100 >= 2:
                            rec.r_extra_hour_25 -= 2
                            hour_100 -= 2
                        if rec.r_extra_hour_25 >= 2 and hour_100 < 2:
                            rec.r_extra_hour_25 -= hour_100
                            hour_100 = 0
                        if rec.r_extra_hour_25 < 2 and hour_100 >= 2:
                            hour_100 -= rec.r_extra_hour_25
                            rec.r_extra_hour_25 = 0
                        if rec.r_extra_hour_25 < 2 and hour_100 < 2:
                            if rec.r_extra_hour_25 > hour_100:
                                rec.r_extra_hour_25 -= hour_100
                                hour_100 = 0
                            else:
                                hour_100 -= rec.r_extra_hour_25
                                rec.r_extra_hour_25 = 0
                        rec.r_extra_hour_35 = rec.r_extra_hour_35 - hour_100 if hour_100 <= rec.r_extra_hour_35 else 0

                if rec.r_hours_compensate > 0:
                    value = 0
                    if not rec.extra_hours_morning:
                        if rec.extra_hour_25 < rec.r_hours_compensate:
                            value = rec.r_hours_compensate - rec.extra_hour_25
                            rec.extra_hour_25 = 0
                        else:
                            rec.extra_hour_25 -= rec.r_hours_compensate
                        rec.extra_hour_35 -= value
                    else:
                        if rec.r_extra_hour_25 < rec.r_hours_compensate:
                            value = rec.r_hours_compensate - rec.r_extra_hour_25
                            rec.r_extra_hour_25 = 0
                        else:
                            rec.r_extra_hour_25 -= rec.r_hours_compensate
                        rec.r_extra_hour_35 -= value

    @api.onchange('hours_compensate')
    def _onchange_hours_compensate(self):
        if self.hours_compensate:
            self.r_hours_compensate = 0

    def action_validate_extra_hours(self):
        for rec in self:
            if rec.extra_hours:
                rec.is_validate_extra_hour = True
