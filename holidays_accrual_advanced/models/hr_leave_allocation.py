import logging
from collections import namedtuple, defaultdict
from math import ceil
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from pytz import utc
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.addons.resource.models.resource import HOURS_PER_DAY
from odoo.tools import float_utils

_logger = logging.getLogger(__name__)
ROUNDING_FACTOR = 16
HrLeaveAllocationAccruementEntry = namedtuple(
    'HrLeaveAllocationAccruementEntry',
    [
        'days_accrued',
        'accrued_on',
        'reason',
    ]
)


class HrLeaveAllocation(models.Model):
    _inherit = 'hr.leave.allocation'

    def _prepare_holiday_values(self, employees):
        self.ensure_one()
        return [{
            'name': self.name,
            'holiday_type': 'employee',
            'holiday_status_id': self.holiday_status_id.id,
            'notes': self.notes,
            'number_of_days': self.number_of_days,
            'parent_id': self.id,
            'employee_id': employee.id,
            'employee_ids': [(6, 0, [employee.id])],
            'state': 'confirm',
            'allocation_type': self.allocation_type,
            'date_from': self.date_from,
            'date_to': self.date_to,
            'accrual_plan_id': self.accrual_plan_id.id,
            'unit_per_interval': self.unit_per_interval,
            'interval_unit': self.interval_unit,
        } for employee in employees]

    unit_per_interval = fields.Selection([
        ('hours', 'Hours'),
        ('days', 'Days')
    ], compute='_compute_from_holiday_status_id', store=True, string="Unit of time added at each interval",
        readonly=False,
        states={'cancel': [('readonly', True)], 'refuse': [('readonly', True)], 'validate1': [('readonly', True)],
                'validate': [('readonly', True)]},
        default=lambda self: self._default_unit_per_interval(),
        help='Units in which Allocation per Accrual Period is defined', )

    interval_unit = fields.Selection([
        ('days', 'Days'),
        ('weeks', 'Weeks'),
        ('months', 'Months'),
        ('years', 'Years')
    ], compute='_compute_from_holiday_status_id', store=True, string="Unit of time between two intervals",
        readonly=False,
        states={'cancel': [('readonly', True)], 'refuse': [('readonly', True)], 'validate1': [('readonly', True)],
                'validate': [('readonly', True)]},
        default=lambda self: self._default_interval_unit(),
        help='Units in which Accrual Period Duration is defined')

    accruement_ids = fields.One2many(
        string='Accruements',
        comodel_name='hr.leave.allocation.accruement',
        inverse_name='leave_allocation_id',
        readonly=True,
    )
    limit_accrued_days = fields.Boolean(
        string='Limit Number of Days Accrued',
        readonly=True,
        states={
            'draft': [('readonly', False)],
            'confirm': [('readonly', False)]
        },
        help=(
            'Limit total maximum number of days accrued in one accrual'
            ' period.'
        ),
    )
    max_accrued_days = fields.Float(
        string='Max Number of Days Accrued',
        readonly=True,
        states={
            'draft': [('readonly', False)],
            'confirm': [('readonly', False)]
        },
        help='Total maximum number of days accrued in one accrual period.',
    )
    limit_carryover_days = fields.Boolean(
        string='Limit Number of Days to Carryover',
        readonly=True,
        states={
            'draft': [('readonly', False)],
            'confirm': [('readonly', False)]
        },
        help=(
            'Limit total maximum number of days to carryover to next accrual'
            ' period.'
        ),
    )
    max_carryover_days = fields.Float(
        string='Max Number of Days to Carryover',
        readonly=True,
        states={
            'draft': [('readonly', False)],
            'confirm': [('readonly', False)]
        },
        help=(
            'Total maximum number of days to carryover to next accrual period.'
        ),
    )
    limit_accumulated_days = fields.Boolean(
        string='Limit Total Balance',
        readonly=True,
        states={
            'draft': [('readonly', False)],
            'confirm': [('readonly', False)]
        },
        help='Limit total maximum number of days that can be accumulated.',
    )
    max_accumulated_days = fields.Float(
        string='Total Balance Limit',
        readonly=True,
        states={
            'draft': [('readonly', False)],
            'confirm': [('readonly', False)]
        },
        help='Total maximum number of days that can be accumulated.',
    )
    accrual_method = fields.Selection(
        selection=[
            ('prorate', 'Prorate'),
            ('period_start', 'At the beginning of the period'),
            ('period_end', 'At the end of the period'),
        ],
        string='Accrual Method',
        default='prorate',
        readonly=True,
        states={
            'draft': [('readonly', False)],
            'confirm': [('readonly', False)]
        },
    )
    accrual_limit = fields.Integer(
        compute='_compute_accrual_limit',
        readonly=True,
    )
    number_per_interval = fields.Float(
        string='Allocation per Accrual Period',
        default=lambda self: self._default_number_per_interval(),
        help=(
            'Allocation accrued per Accrual Period, measured in'
            ' Allocation Units'
        ),
    )
    interval_number = fields.Integer(
        string='Accrual Period Duration',
        default=lambda self: self._default_interval_number(),
        help=(
            'Duration of a single accrual period, measured in'
            ' Accrual Period Units'
        ),
    )

    @api.model
    def _default_number_per_interval(self):
        return 20.0

    @api.model
    def _default_interval_number(self):
        return 1

    @api.model
    def _default_unit_per_interval(self):
        return 'days'

    @api.model
    def _default_interval_unit(self):
        return 'years'

    @api.onchange('holiday_type')
    def _onchange_holiday_type(self):  # pragma: no cover
        if self.holiday_type != 'employee':
            self.allocation_type = 'regular'

    @api.depends('limit_accumulated_days', 'max_accumulated_days')
    def _compute_accrual_limit(self):
        for allocation in self:
            if allocation.limit_accumulated_days:
                allocation.accrual_limit = ceil(
                    allocation.max_accumulated_days
                )
            else:
                allocation.accrual_limit = 0

    def action_recalculate_accrual_allocations(self):
        for allocation in self:
            employee = allocation.employee_id
            if employee:
                if employee.contract_id:
                    if employee.contract_id.state == 'open':
                        allocation._update_accrual_allocation()

    @api.model
    def action_recalculate_accrual_allocations_all(self):
        allocations = self.search([
            ('allocation_type', '=', 'accrual'),
            ('state', '=', 'validate'),
            ('holiday_type', '=', 'employee')
        ])

        for allocation in allocations:
            allocation._update_accrual_allocation()

    @api.model
    def create(self, values):
        if 'holiday_type' in values and values['holiday_type'] != 'employee':
            values['allocation_type'] = 'regular'

        accrual = values.get('allocation_type') and values['allocation_type'] == 'accrual'
        date_from = values.get('date_from', None)

        result = super().create(values)

        if accrual:
            result.filtered(lambda x: x.date_from != date_from).write({'date_from': date_from})
        return result

    def write(self, values):
        if 'holiday_type' in values and values['holiday_type'] != 'employee':
            values['allocation_type'] = 'regular'
        return super().write(values)

    def _update_accrual(self):
        super()._update_accrual()

        allocations = self.search([
            ('allocation_type', '=', 'accrual'),
            ('state', '=', 'validate'),
            ('holiday_type', '=', 'employee')
        ])

        for allocation in allocations:
            allocation._update_accrual_allocation()

    def _update_accrual_allocation(self):
        self.ensure_one()

        if not self.allocation_type == 'accrual':  # pragma: no cover
            raise UserError(_('Only accrual allocations can be recalculated'))

        accruements, number_of_days = self._calculate_accrued_amount(
            datetime.combine(
                datetime.today(),
                datetime.min.time()
            )
        )

        accruement_ids = [(5, False, False)]
        for accruement in accruements:
            accruement_ids.append((0, False, {
                'days_accrued': accruement.days_accrued,
                'accrued_on': accruement.accrued_on,
                'reason': accruement.reason,
            }))

        self.with_context({
            'mail_notrack': True,
        }).write({
            'number_of_days': number_of_days,
            'accruement_ids': accruement_ids,
        })

    def _calculate_accrued_amount(self, as_of_datetime):
        self.ensure_one()

        period = self._get_accrual_period()
        date_from = self._get_date_from()
        date_to = self._get_date_to()

        if not date_to or date_to > as_of_datetime:
            date_to = as_of_datetime

        _logger.info(
            'Calculating "%s" leave allocation for employee "%s" between %s and %s with %s period as of %s',
            self.holiday_status_id.display_name,
            self.employee_id.display_name,
            date_from,
            date_to,
            period,
            as_of_datetime,
        )

        balance = 0.0
        total_leave_days = 0.0
        accruements = []
        while date_from < date_to:
            if self.limit_carryover_days and balance > self.max_carryover_days:
                loss = self.max_carryover_days - balance
                accruements.append(HrLeaveAllocationAccruementEntry(
                    days_accrued=loss,
                    accrued_on=date_from.date(),
                    reason=_('Loss due to period carry-over limit')
                ))
                balance += loss

            period_start = date_from
            period_end = min(period_start + period, date_to)

            worked_days = self._get_worked_days(
                period_start,
                period_end,
            )
            workable_days = self._get_workable_days(
                period_start,
                period_start + period,
            )
            leave_days = self._get_leave_days(
                period_start,
                period_end,
            )

            _logger.info(
                'Employee "%s" / allocation %s (%s - %s): %s days worked, %s workable days, %s leave days',
                self.employee_id.name,
                self.holiday_status_id.name,
                period_start,
                period_end,
                worked_days,
                workable_days,
                leave_days,
            )

            accruement = self._get_days_to_accrue(
                period_start,
                period,
                period_end,
                as_of_datetime,
                worked_days,
                workable_days
            )
            if accruement:
                accruements.append(accruement)
                balance += accruement.days_accrued

                if self.limit_accrued_days and accruement.days_accrued > self.max_accrued_days:
                    loss = self.max_accrued_days - accruement.days_accrued
                    accruements.append(HrLeaveAllocationAccruementEntry(
                        days_accrued=loss,
                        accrued_on=accruement.accrued_on,
                        reason=_('Loss due to accrued amount limit')
                    ))
                    balance += loss

                if self.limit_accumulated_days and balance > self.max_accumulated_days:
                    loss = self.max_accumulated_days - balance
                    accruements.append(HrLeaveAllocationAccruementEntry(
                        days_accrued=loss,
                        accrued_on=accruement.accrued_on,
                        reason=_('Loss due to accumulation limit')
                    ))
                    balance += loss
            # discount leaves
            # if leave_days > 0:
            #     accruements.append(HrLeaveAllocationAccruementEntry(
            #         days_accrued=-leave_days,
            #         accrued_on=period_end.date(),
            #         reason=_('Usage during accruement period')
            #     ))
            #     balance -= leave_days
            #     total_leave_days += leave_days

            date_from += period

        number_of_days = balance + total_leave_days
        _logger.info(
            '%s day(s) of "%s" leave allocated to employee "%s"',
            number_of_days,
            self.holiday_status_id.name,
            self.employee_id.name,
        )

        return accruements, number_of_days

    def _get_worked_days(self, from_datetime, to_datetime):
        """
        Compute number of worked days, that is computed as number workable days
        without unpaid leaves (that are not on global leaves) counted in.
        """
        self.ensure_one()

        # NOTE: This mimics ResourceMixin.get_work_days_data() w/ changes

        calendar = self.employee_id.resource_calendar_id

        if not from_datetime.tzinfo:
            from_datetime = from_datetime.replace(tzinfo=utc)
        if not to_datetime.tzinfo:
            to_datetime = to_datetime.replace(tzinfo=utc)

        # total hours per day: retrieve attendances with one extra day margin,
        # in order to compute the total hours on the first and last days

        resource_intervals = self.employee_id.resource_id if self.employee_id.resource_id else self.env[
            'resource.resource']
        intervals = calendar._attendance_intervals_batch(
            from_datetime - timedelta(days=1),
            to_datetime + timedelta(days=1),
            resource_intervals,
        )[resource_intervals.id]
        day_total = defaultdict(float)
        for start, stop, meta in intervals:
            day_total[start.date()] += (stop - start).total_seconds() / 3600

        # actual hours per day
        attendance_intervals = calendar._attendance_intervals_batch(
            from_datetime,
            to_datetime,
            resource_intervals,
        )[resource_intervals.id]
        unpaid_intervals = calendar._leave_intervals(
            from_datetime,
            to_datetime,
            self.employee_id.resource_id,
            domain=[
                ('unpaid', '=', True),
                ('time_type', '=', 'leave')
            ],
        )
        global_intervals = calendar._leave_intervals(
            from_datetime,
            to_datetime,
            None,
        )
        intervals = (
                attendance_intervals - (unpaid_intervals - global_intervals)
        )
        day_hours = defaultdict(float)
        for start, stop, meta in intervals:
            day_hours[start.date()] += (stop - start).total_seconds() / 3600

        # compute number of days as quarters
        return sum(
            float_utils.round(
                ROUNDING_FACTOR * day_hours[day] / day_total[day]
            ) / ROUNDING_FACTOR
            for day in day_hours
        )

    def _get_workable_days(self, from_datetime, to_datetime):
        """
        Compute number of workable days, that is computed from calendar and
        configured attendances only.
        """
        self.ensure_one()

        return self.employee_id.get_work_days_data(
            from_datetime,
            to_datetime,
            compute_leaves=False,
        )['days']

    def _get_leave_days(self, from_datetime, to_datetime):
        """
        Compute number of days on used from the allocation, without global
        leaves taken into account, other leaves are irrelevant since it's
        ensured that no two leaves overlap.
        """
        self.ensure_one()

        # NOTE: This mimics ResourceMixin.get_leave_days_data() w/ changes

        calendar = self.employee_id.resource_calendar_id

        if not from_datetime.tzinfo:
            from_datetime = from_datetime.replace(tzinfo=utc)
        if not to_datetime.tzinfo:
            to_datetime = to_datetime.replace(tzinfo=utc)

        # total hours per day: retrieve attendances with one extra day margin,
        # in order to compute the total hours on the first and last days

        resource_intervals = self.employee_id.resource_id if self.employee_id.resource_id else self.env[
            'resource.resource']
        intervals = calendar._attendance_intervals_batch(
            from_datetime - timedelta(days=1),
            to_datetime + timedelta(days=1),
            resource_intervals,
        )[resource_intervals.id]
        day_total = defaultdict(float)
        for start, stop, meta in intervals:
            day_total[start.date()] += (stop - start).total_seconds() / 3600

        # actual hours per day
        attendance_intervals = calendar._attendance_intervals_batch(
            from_datetime,
            to_datetime,
            resource_intervals,
        )[resource_intervals.id]
        leave_intervals = calendar._leave_intervals(
            from_datetime,
            to_datetime,
            self.employee_id.resource_id,
            domain=[
                ('holiday_status_id', '=', self.holiday_status_id.id),
                ('time_type', '=', 'leave')
            ],
        )
        global_intervals = calendar._leave_intervals(
            from_datetime,
            to_datetime,
            None,
        )
        intervals = (
                attendance_intervals & (leave_intervals - global_intervals)
        )
        day_hours = defaultdict(float)
        for start, stop, meta in intervals:
            day_hours[start.date()] += (stop - start).total_seconds() / 3600

        # compute number of days as quarters
        return sum(
            float_utils.round(
                ROUNDING_FACTOR * day_hours[day] / day_total[day]
            ) / ROUNDING_FACTOR
            for day in day_hours
        )

    def _get_accrual_period(self):
        self.ensure_one()

        if self.interval_unit == 'weeks':
            return relativedelta(weeks=self.interval_number)
        elif self.interval_unit == 'months':
            return relativedelta(months=self.interval_number)
        elif self.interval_unit == 'years':
            return relativedelta(years=self.interval_number)

    def _get_date_from(self):
        self.ensure_one()

        if self.date_from:
            return datetime.combine(self.date_from, datetime.min.time())
        return self.employee_id.create_date

    def _get_date_to(self):
        self.ensure_one()

        if self.date_to:
            return datetime.combine(self.date_to, datetime.min.time())

        return None

    def _get_days_to_accrue(self, period_start, period, period_end, as_of_datetime, days_worked, workable_days):
        self.ensure_one()

        days_to_accrue = self.number_per_interval
        if self.unit_per_interval == 'hours':
            days_to_accrue /= self.employee_id.resource_calendar_id.hours_per_day or HOURS_PER_DAY

        if self.accrual_method == 'period_start' and period_start < as_of_datetime:
            return HrLeaveAllocationAccruementEntry(
                days_accrued=days_to_accrue,
                accrued_on=period_start.date(),
                reason=_('Start-of-period accruement')
            )
        elif self.accrual_method == 'period_end' and period_start + period < as_of_datetime:
            return HrLeaveAllocationAccruementEntry(
                days_accrued=days_to_accrue,
                accrued_on=period_end.date(),
                reason=_('End-of-period accruement')
            )
        elif self.accrual_method == 'prorate' and workable_days > 0:
            return HrLeaveAllocationAccruementEntry(
                days_accrued=days_to_accrue * (days_worked / workable_days),
                accrued_on=period_end.date(),
                reason=_('Prorate accruement for %s of %s days') % (
                    days_worked,
                    workable_days,
                )
            )
        return None
