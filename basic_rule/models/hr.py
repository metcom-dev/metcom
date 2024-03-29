from odoo import api, fields, models
from datetime import datetime
from dateutil.relativedelta import relativedelta


class HrWorkEntry(models.Model):
    _inherit = 'hr.work.entry'

    def _get_duration_is_valid(self):
        return False


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    holidays_per_year = fields.Char(
        string='Días de vacaciones por año',
        groups='hr.group_hr_user'
    )

    no_provide_pension = fields.Boolean(
        string='No aporta pensión',
        default=False,
        groups='hr.group_hr_user')

    def _check_no_apply_afp_premium(self):
        return True if self.age >= 65.0 and not self.indicator else False

    no_apply_afp_premium = fields.Boolean(
        string='No aplica prima AFP',
        default=lambda self: self._check_no_apply_afp_premium(),
        groups='hr.group_hr_user'
    )
    age = fields.Float(string='Edad', compute="_compute_age", groups='hr.group_hr_user')
    indicator = fields.Boolean(default=False, groups='hr.group_hr_user')

    @api.depends("birthday")
    def _compute_age(self):
        for record in self:
            age = relativedelta(datetime.now(), record.birthday)
            record.age = age.years + (age.months / 12)

    upper = fields.Char(compute='_compute_upper',
                        inverse='_inverse_upper',
                        search='_search_upper')

    @api.onchange('age')
    def _compute_onchange_no_apply_afp_premium(self):
        for rec in self:
            if rec.age >= 65.0 and not rec.indicator:
                rec.no_apply_afp_premium = True
                rec.indicator = True

    def _inverse_no_apply_afp_premium(self):
        pass


class HrContract(models.Model):
    _inherit = 'hr.contract'

    advance_percent = fields.Float(
        string='Porcentaje de Anticipo'
    )


class HrSalaryRule(models.Model):
    _inherit = 'hr.salary.rule'

    apply_advance_payroll = fields.Boolean(string='¿Aplica nómina de adelanto?')


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    def get_order_periods(self, periods):
        """
        :param periods: list of periods with this string format: mm/YYYY
        :return: list of ordered periods
        """
        new_periods = []
        for period in periods:
            _, last_day = self.env['hr.payslip'].get_month_day_range(period)
            new_periods.append(last_day)
        new_periods.sort()
        periods = [val.strftime('%m/%Y') for val in new_periods]
        return periods

    def _get_base_local_dict(self):
        """
        Pass hr.payslip id to specific searches in computed rule
        """

        res = super()._get_base_local_dict()
        res.update({
            'slip_id': self._origin.id
        })
        return res

    @staticmethod
    def _get_month(year, month, value_month):
        value = month - value_month
        if value < 0:
            new_month = 12 + value
            new_year = year - 1
        elif value == 0:
            new_month = 12
            new_year = year - 1
        else:
            new_month = value
            new_year = year
        return new_month, new_year

    def _get_periods(self, start_m, start_y, end_m, end_y):
        periods = self.env['hr.payslip.line']._get_periods(start_m, start_y, end_m, end_y)
        return periods

    def _get_months_before(self, months_before):
        month = int(self.month)
        year = int(self.year)
        start_m, star_y = self._get_month(year, month, months_before)
        end_m, end_y = self._get_month(year, month, 1)
        periods = self._get_periods(start_m, star_y, end_m, end_y)
        return periods

    @staticmethod
    def get_month_day_range(period):
        """
        :param period: month with format : mm/YYYY => Ex: 06/20
        :return: Return initial and final date of some period
        """
        datetime_str = '{}-{}-01 15:00:00'.format(period[3:], period[0:2])
        datetime_object = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S').date()
        last_day = datetime_object + relativedelta(day=1, months=+1, days=-1)
        first_day = datetime_object + relativedelta(day=1)
        return first_day, last_day

    def get_inputs_data(self):
        res = super(HrPayslip, self).get_inputs_data()
        if not res:
            return res

        advance_percent = self.contract_id.advance_percent
        for r in res:
            if r['code'] == 'NQA_001' and r['contract_id'] == self.contract_id.id:
                r['amount'] = advance_percent
        return res
