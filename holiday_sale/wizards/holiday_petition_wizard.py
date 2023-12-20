from dateutil.relativedelta import relativedelta
from odoo import models, fields, api
from odoo.exceptions import ValidationError
import pytz
from datetime import datetime


def _convert_date_timezone_to_utc(user, date_order, format_time='%Y-%m-%d %H:%M:%S'):
    tz = pytz.timezone(user.tz) if user.tz else pytz.utc
    date_order = datetime.strptime(date_order, format_time)
    datetime_with_tz = tz.localize(date_order, is_dst=None)
    date_order = datetime_with_tz.astimezone(pytz.utc)
    date_order = datetime.strftime(date_order, format_time)
    return date_order


class HrLeave(models.Model):
    _inherit = 'hr.leave'

    date_from_wizard = fields.Date(
        string='Desde'
    )
    date_to_wizard = fields.Date(
        string='Hasta'
    )


class HrEmployeeBase(models.AbstractModel):
    _inherit = "hr.employee.base"

    def _compute_leave_status(self):
        # Used SUPERUSER_ID to forcefully get status of other user's leave, to bypass record rule
        holidays = self.env['hr.leave'].sudo().search([
            ('employee_id', 'in', self.ids),
            ('date_from', '<=', fields.Datetime.now()),
            ('date_to', '>=', fields.Datetime.now()),
            ('state', 'not in', ('cancel', 'refuse'))
        ])
        leave_data = {}
        for holiday in holidays:
            leave_data[holiday.employee_id.id] = {}
            leave_data[holiday.employee_id.id]['leave_date_from'] = holiday.date_from.date()
            leave_data[holiday.employee_id.id]['leave_date_to'] = holiday.date_to.date()
            leave_data[holiday.employee_id.id]['current_leave_state'] = holiday.state
            leave_data[holiday.employee_id.id]['holiday_status_code'] = holiday.holiday_status_id.code

        for employee in self:
            employee.leave_date_from = leave_data.get(employee.id, {}).get('leave_date_from')
            employee.leave_date_to = leave_data.get(employee.id, {}).get('leave_date_to')
            employee.current_leave_state = leave_data.get(employee.id, {}).get('current_leave_state')

            employee.is_absent = leave_data.get(employee.id) and leave_data.get(employee.id, {}).get(
                'current_leave_state') in ['validate'] and leave_data.get(employee.id, {}).get(
                'holiday_status_code') != '90'


class HolidayPetitionWizard(models.TransientModel):
    _inherit = 'holiday.petition.wizard'

    employee_id = fields.Many2one()

    holiday_status_id = fields.Many2one(
        comodel_name='hr.leave.type',
        string='Tipo de Ausencia',
        default=lambda self: self.env.ref('holiday_process.hr_leave_type_23'),
        required=True,
        readonly=False
    )

    hr_leave_id = fields.Many2one(
        comodel_name='hr.leave.allocation',
        string='Asignación',
    )

    date_from = fields.Date(
        string='Desde'
    )
    date_to = fields.Date(
        string='Hasta'
    )
    holiday_status_code = fields.Char(
        related='holiday_status_id.code',
        string='Código de Ausencia'
    )

    @api.onchange('employee_id')
    def checker(self):
        if self.employee_id != self.hr_leave_id.employee_id:
            self.hr_leave_id = None

    @api.depends('employee_id', 'holiday_status_id')
    def _compute_allocation_ids(self):
        for rec in self:
            if rec.employee_id and rec.holiday_status_id:
                allocation_ids = self.env['hr.leave.allocation'].search([
                    ('employee_id', '=', rec.employee_id.id),
                    ('pending_holiday', '>', 0)
                ])
                rec.allocation_ids = allocation_ids
            else:
                rec.allocation_ids = False

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(HolidayPetitionWizard, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        if view_type == 'form':
            leave1 = self.env.ref('holiday_process.hr_leave_type_23')
            leave2 = self.env.ref('holiday_sale.hr_leave_type_90')
            res['fields']['holiday_status_id']['domain'] = [('id', 'in', [leave1.id, leave2.id])]
        return res

    @api.onchange('nro_holidays', 'from_date')
    def _onchange_date_from(self):
        if self.nro_holidays and self.from_date:
            self.date_from = self.from_date + relativedelta(days=1)

    @api.onchange('nro_holidays', 'from_date')
    def _onchange_date_to(self):
        if self.nro_holidays and self.from_date:
            self.date_to = self.from_date + relativedelta(days=self.nro_holidays)

    @api.constrains('date_from', 'date_to')
    def _check_dates_compensation(self):
        for rec in self:
            if rec.date_from and rec.date_to:
                if rec.date_from > rec.date_to:
                    raise ValidationError('La fecha "Desde" no puede ser mayor que la fecha "Hasta".')

    def action_generate_holidays(self):
        if self.nro_holidays <= 0:
            raise ValidationError('El número de días de vacaciones no pueden ser menor o igual a 0.')

        if self.hr_leave_id:
            if self.nro_holidays > self.hr_leave_id.pending_holiday:
                raise ValidationError(
                    'El número de días de vacaciones no pueden ser mayor a los dias pendientes del registro seleccionado')

            if 0 > self.hr_leave_id.pending_holiday:
                raise ValidationError('No se puede usar un registro sin dias pendientes')

        hr_leave_type = self.env['hr.leave.type'].search([('name', '=', 'Vacaciones a Liquidar')])
        if not hr_leave_type:
            hr_leave_type = self.env['hr.leave.type'].create({
                'name': 'Vacaciones a Liquidar',
            })
            vac_lbs_code = self.env['hr.work.entry.type'].search([('code', '=', 'VAC_LBS')])
            hr_leave_type.write({'work_entry_type_id': vac_lbs_code.id})

        for record in self:
            
            if record.is_settlement:
                record.holiday_status_id = hr_leave_type.id
            else:
                hr_id_leave_type = self.env['hr.leave.type'].search([('id','=',self.holiday_status_id.id)])
                hr_id_leave_type.write({"work_entry_type_id":hr_id_leave_type.work_entry_type_id.id})
                
                                         
        hr_allocation_ids = self.allocation_ids
        nro = self.nro_holidays
        total_pending_holiday = sum(line.pending_holiday for line in hr_allocation_ids)
        context = {
            'default_is_generated': True,
            'default_employee_id': self.employee_id.id,
            'default_from_date': self.from_date,
            'default_to_date': self.to_date,
            'default_holiday_status_id': self.holiday_status_id.id,
        }

        if total_pending_holiday < nro:
            context.update({
                'default_msj': 'La sumatoria total de días pendientes de las asignaciones "{}"'
                               ' es menor que la cantidad de días a asignar "{}".'.format(total_pending_holiday, nro)
            })
        else:
            absences = []
            request_date_from = self.from_date
            if self.hr_leave_id:
                days = self.hr_leave_id.pending_holiday if nro >= self.hr_leave_id.pending_holiday else nro
                absence_id = self.create_holiday_absences(request_date_from, days, self.hr_leave_id)
                absences.append(absence_id.id)
                if not self._context.get('settlement'):
                    request_date_from += relativedelta(days=days)
                nro -= days
                if nro <= 0 and self._context.get('settlement'):
                    self.hr_leave_id.date_to = absence_id.date_to

            else:
                for allocation in hr_allocation_ids.sorted(key=lambda r: r.from_date):
                    if nro > 0:
                        days = allocation.pending_holiday if nro >= allocation.pending_holiday else nro
                        absence_id = self.create_holiday_absences(request_date_from, days, allocation)
                        absences.append(absence_id.id)
                        if not self._context.get('settlement'):
                            request_date_from += relativedelta(days=days)
                        nro -= days
                        if nro <= 0 and self._context.get('settlement'):
                            allocation.date_to = absence_id.date_to
                            break

            context.update({
                'default_absence_ids': absences,
            })
        return self.action_reopen_wizard(context=context)

    def create_holiday_absences(self, from_date, total_days, allocation_id):
        to_date = from_date + relativedelta(days=total_days)
        absence_id = self.env['hr.leave'].create({
            'holiday_status_id': self.holiday_status_id.id,
            'employee_id': self.employee_id.id,
            'holiday_type': 'employee',
            'hr_leave_id': allocation_id.id, 'request_date_to': to_date,
            'request_date_from': from_date,
            # minutes are not zero because when it's the same date compute do not calc one day
            'date_from_wizard': self.date_from,
            'date_to_wizard': self.date_to,
            'date_from': datetime.combine(from_date, datetime.min.time()),
            'date_to': datetime.combine(to_date, datetime.min.time())
        })
        if self._context.get('settlement'):
            absence_id.name = """Esta ausencia no ha sido gozada, sino que se ha creado para dejar constancia que ya se han pagado por medio de una compra o liquidación."""
            self.env['hr.leave'].search([('id', '=', absence_id.id)]).write({
                'number_of_days': total_days
            })
        return absence_id
