from datetime import datetime
from odoo import api, fields, models


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    def _get_worked_day_lines(self, domain=None, check_out_of_contract=True):
        res = super(HrPayslip, self)._get_worked_day_lines(domain, check_out_of_contract)
        if self.contract_id.resource_calendar_id:
            service_start_date = self.contract_id.employee_id.service_start_date
            if service_start_date:
                hours_per_day = self.contract_id.resource_calendar_id.hours_per_day or 0.0
                date_start, year, month, _ = self.generate_date_start_month_year(self.date_from, self.date_to)
                month = int(month)
                year = int(year)
                start_m, star_y = self._get_month(year, month, 6)
                end_m, end_y = self._get_month(year, month, 1)
                periods = self._get_periods(start_m, star_y, end_m, end_y)
                service_date = '{}/{}'.format(service_start_date.strftime('%m'), service_start_date.strftime('%Y'))

                worked_lines = self.env['hr.payslip.worked_days'].search([
                    ('date_start', 'in', periods),
                    ('employee_id', '=', self.employee_id.id),
                    ('number_of_days', '>', 0)
                ])

                # TDI_001
                tdi_001_days = self.get_calc_tdi_days(worked_lines, periods, 'TDI_001')
                tdi_001_hours = tdi_001_days * hours_per_day
                tdi_001_entry_type_id = self.env.ref('legal_benefits_rule.hr_work_entry_type_tdi_001')

                # TDI_002
                tdi_002_days = self.get_calc_tdi_days(worked_lines, periods, 'TDI_002')
                tdi_002_hours = tdi_002_days * hours_per_day
                tdi_002_entry_type_id = self.env.ref('legal_benefits_rule.hr_work_entry_type_tdi_002')

                # TDL_001
                tdl_001_days = self.get_calc_tdl_days(worked_lines, periods, 'TDL_001')
                tdl_001_hours = tdl_001_days * hours_per_day
                tdl_001_entry_type_id = self.env.ref('legal_benefits_rule.hr_work_entry_type_tdl_001')

                # TDL_002
                tdl_002_days = self.get_calc_tdl_days(worked_lines, periods, 'TDL_002')
                tdl_002_hours = tdl_002_days * hours_per_day
                tdl_002_entry_type_id = self.env.ref('legal_benefits_rule.hr_work_entry_type_tdl_002')

                # TDM_001
                health_periods = self._get_periods(11, year - 1, end_m, end_y)
                h_lines = self.env['hr.payslip.worked_days'].search([
                    ('date_start', 'in', health_periods),
                    ('employee_id', '=', self.employee_id.id),
                    ('number_of_days', '>', 0)
                ])
                tdm_001 = h_lines.filtered(lambda x: x.code == 'TDM_001' and x.date_start != health_periods[0])
                tdm_001 = sum(line.number_of_days for line in tdm_001)

                code_20 = h_lines.filtered(lambda x: x.code == '20')
                code_20 = sum(line.number_of_days for line in code_20)

                tdm_001_days = code_20 - 60 if code_20 > 60 else 0
                tdm_001_days -= tdm_001
                tdm_001_hours = tdm_001_days * hours_per_day
                tdm_001_entry_type_id = self.env.ref('legal_benefits_rule.hr_work_entry_type_tdm_001')

                # MES_004
                new_periods = list(set(worked_lines.mapped('date_start')))
                new_periods = self.env['hr.payslip'].get_order_periods(new_periods)
                if month == 12:
                    except_period = '{}/{}'.format("{:02d}".format(start_m), star_y)
                    new_periods = list(filter(lambda w: w != except_period, new_periods))
                tmp_periods = []
                flag = False
                service_date_in_periods = True if service_date in new_periods else False
                for p in new_periods:
                    if not flag and (not service_date_in_periods or p == service_date):
                        flag = True
                    if flag:
                        tmp_periods.append(p)
                if tmp_periods and service_start_date.strftime('%Y') == tmp_periods[0][3:] and \
                        service_start_date.strftime('%m') == tmp_periods[0][:2]:
                    if service_start_date.strftime('%d') == 1:
                        mes_004_days = len(tmp_periods)
                    else:
                        mes_004_days = len(tmp_periods) - 1
                else:
                    mes_004_days = len(tmp_periods)
                mes_004_days *= 30

                if month == 12:
                    mes_004_days += 30
                mes_001_days = 0
                dias_002_days = 0

                # DIAS_003
                dias_003_days = self._get_calc_dias_003(worked_lines, self.contract_id.employee_id, date_start)
                dias_003_hours = dias_003_days * hours_per_day
                dias_003_entry_type_id = self.env.ref('legal_benefits_rule.hr_work_entry_type_dias_003')

                # MES_001 DIAS_002
                if worked_lines:
                    i = 0
                    for period in periods:
                        if service_date != period:
                            i += 1 if worked_lines.filtered(lambda x: x.date_start == period) else 0
                    if i > 1:
                        mes_001_days = i * 30

                start_m, start_y = self._get_month(year, month, 7)
                new_period = '{}/{}'.format("{:02d}".format(start_m), start_y)
                worked_lines += self.env['hr.payslip.worked_days'].search([
                    ('date_start', '=', new_period),
                    ('employee_id', '=', self.employee_id.id),
                    ('number_of_days', '>', 0)
                ])

                if worked_lines:
                    period_contract = worked_lines.filtered(lambda x: x.date_start == service_date)
                    if period_contract:
                        _, service_end_date = self.env['hr.payslip'].get_month_day_range(service_date)
                        dias_002_days = (service_end_date - service_start_date).days

                # DIAS_002
                dias_002_hours = dias_002_days * hours_per_day
                dias_002_entry_type_id = self.env.ref('legal_benefits_rule.hr_work_entry_type_dias_002')

                # MES_001
                mes_001_hours = mes_001_days * hours_per_day
                mes_001_entry_type_id = self.env.ref('legal_benefits_rule.hr_work_entry_type_mes_001')

                # MES_002
                periods.append(date_start)
                mes_002_days = self._get_calc_cts_grat_per_days(periods, self.contract_id, date_start, month, 'CTS_002')
                mes_002_hours = mes_002_days * hours_per_day
                mes_002_entry_type_id = self.env.ref('legal_benefits_rule.hr_work_entry_type_mes_002')

                # MES_003
                mes_003_days = self._get_calc_cts_grat_per_days(periods, self.contract_id, date_start, month, 'GRAT_001')
                mes_003_hours = mes_003_days * hours_per_day
                mes_003_entry_type_id = self.env.ref('legal_benefits_rule.hr_work_entry_type_mes_003')

                # MES_004
                mes_004_hours = mes_004_days * hours_per_day
                mes_004_entry_type_id = self.env.ref('legal_benefits_rule.hr_work_entry_type_mes_004')

                values = [{
                    'sequence': tdi_001_entry_type_id.sequence, 'work_entry_type_id': tdi_001_entry_type_id.id, 'number_of_days': tdi_001_days,
                    'number_of_hours': tdi_001_hours
                }, {
                    'sequence': tdi_002_entry_type_id.sequence, 'work_entry_type_id': tdi_002_entry_type_id.id, 'number_of_days': tdi_002_days,
                    'number_of_hours': tdi_002_hours
                }, {
                    'sequence': tdl_001_entry_type_id.sequence, 'work_entry_type_id': tdl_001_entry_type_id.id, 'number_of_days': tdl_001_days,
                    'number_of_hours': tdl_001_hours
                }, {
                    'sequence': tdl_002_entry_type_id.sequence, 'work_entry_type_id': tdl_002_entry_type_id.id, 'number_of_days': tdl_002_days,
                    'number_of_hours': tdl_002_hours
                }, {
                    'sequence': tdm_001_entry_type_id.sequence, 'work_entry_type_id': tdm_001_entry_type_id.id, 'number_of_days': tdm_001_days,
                    'number_of_hours': tdm_001_hours
                }, {
                    'sequence': dias_002_entry_type_id.sequence, 'work_entry_type_id': dias_002_entry_type_id.id, 'number_of_days': dias_002_days,
                    'number_of_hours': dias_002_hours
                }, {
                    'sequence': dias_003_entry_type_id.sequence, 'work_entry_type_id': dias_003_entry_type_id.id, 'number_of_days': dias_003_days,
                    'number_of_hours': dias_003_hours
                }, {
                    'sequence': mes_001_entry_type_id.sequence, 'work_entry_type_id': mes_001_entry_type_id.id, 'number_of_days': mes_001_days,
                    'number_of_hours': mes_001_hours
                }, {
                    'sequence': mes_002_entry_type_id.sequence, 'work_entry_type_id': mes_002_entry_type_id.id, 'number_of_days': mes_002_days,
                    'number_of_hours': mes_002_hours
                }, {
                    'sequence': mes_003_entry_type_id.sequence, 'work_entry_type_id': mes_003_entry_type_id.id, 'number_of_days': mes_003_days,
                    'number_of_hours': mes_003_hours
                }, {
                    'sequence': mes_004_entry_type_id.sequence, 'work_entry_type_id': mes_004_entry_type_id.id, 'number_of_days': mes_004_days,
                    'number_of_hours': mes_004_hours
                }]
                res += values
        return res

    def get_calc_tdi_days(self, worked_lines, periods, code):
        line_tdi = worked_lines.filtered(lambda x: x.code == code)
        if line_tdi:
            new_periods = self.get_new_periods(periods, line_tdi[0].date_start)
            tdi_lines = worked_lines.filtered(
                lambda x: x.date_start in new_periods and x.is_benefits_license_absence)
        else:
            tdi_lines = worked_lines.filtered(lambda x: x.is_benefits_license_absence)
        tdi_days = sum(line.number_of_days for line in tdi_lines)
        return tdi_days

    def get_calc_tdl_days(self, worked_lines, periods, code):
        line_tdl = worked_lines.filtered(lambda x: x.code == code)
        if line_tdl:
            new_periods = self.get_new_periods(periods, line_tdl[0].date_start)
            tdl_lines = worked_lines.filtered(
                lambda x: x.date_start in new_periods and x.is_social_benefits_license)
        else:
            tdl_lines = worked_lines.filtered(lambda x: x.is_social_benefits_license)
        tdl_days = sum(line.number_of_days for line in tdl_lines)
        return tdl_days

    def _get_calc_dias_003(self, worked_lines, employee_id, date_start):
        dias_003_days = 0
        service_start_date = employee_id.service_start_date
        service_termination_date = employee_id.service_termination_date
        service_date = '{}/{}'.format(service_start_date.strftime('%m'), service_start_date.strftime('%Y'))

        filter_dias_003 = worked_lines.filtered(lambda x: x.date_start == service_date)
        day_service_start_date = int(service_start_date.strftime('%d'))
        if filter_dias_003 and day_service_start_date > 1:
            dias_003_days += abs(30 - day_service_start_date)
        if service_termination_date:
            worked_lines += self.env['hr.payslip.worked_days'].search([
                ('date_start', '=', date_start),
                ('employee_id', '=', employee_id.id),
                ('number_of_days', '>', 0)
            ])
            termination_date = '{}/{}'.format(service_termination_date.strftime('%m'), service_termination_date.strftime('%Y'))
            if service_termination_date and termination_date != service_date:
                filter_dias_003 = worked_lines.filtered(lambda x: x.date_start == termination_date)
                day_service_termination_date = int(service_termination_date.strftime('%d'))
                if filter_dias_003 and day_service_termination_date < 30:
                    dias_003_days += day_service_termination_date
        return dias_003_days

    def _get_calc_cts_grat_per_days(self, periods, contract_id, date_start, month, code):
        worked_days_ids = self.env['hr.payslip.worked_days'].search([
            ('date_start', 'in', periods),
            ('employee_id', '=', contract_id.employee_id.id),
            ('number_of_hours', '>', 0)
        ], order='date_start_dt desc')
        periods = list(set(worked_days_ids.mapped('date_start')))
        periods = self.env['hr.payslip'].get_order_periods(periods)

        slip_line_ids = self.env['hr.payslip.line'].search([
            ('date_start', 'in', periods),
            ('employee_id', '=', contract_id.employee_id.id),
            ('amount', '>', 0),
            ('code', '=', code)
        ], limit=1, order='date_start_dt desc')
        periods = list(set(worked_days_ids.mapped('date_start')))
        periods = self.env['hr.payslip'].get_order_periods(periods)

        new_periods = []
        service_start_date = contract_id.employee_id.service_start_date
        service_termination_date = contract_id.employee_id.service_termination_date
        service_start_day = service_start_date.strftime('%d')
        service_date_s = '{}/{}'.format(service_start_date.strftime('%m'), service_start_date.strftime('%Y'))

        service_termination_day = int(service_termination_date.strftime('%d')) if service_termination_date else 0
        service_date_t = '{}/{}'.format(service_termination_date.strftime('%m'), service_termination_date.strftime(
            '%Y')) if service_termination_date else False

        for period in periods:
            if slip_line_ids and period == slip_line_ids.date_start and period[0:2] in ['12', '07']:
                break
            else:
                new_periods.append(period)

        if service_start_day != '01':
            new_periods = list(filter(lambda d: d != service_date_s, new_periods))
        if service_termination_date and date_start == service_date_t and service_termination_day < 31 and month != 12:
            new_periods = list(filter(lambda d: d != service_date_t, new_periods))
        len_periods = len(new_periods)
        days = len_periods * 30
        return days

    @staticmethod
    def get_new_periods(periods, min_period):
        found = False
        new_periods = []
        for rec in periods:
            if min_period == rec:
                found = True
            if found:
                new_periods.append(rec)
        return new_periods

    def get_inputs_data(self):
        res = super(HrPayslip, self).get_inputs_data()
        if not res:
            return res
        analytic_lines = self.env['account.analytic.line'].search([
            ('pay_date', '!=', False),
            ('pay_date', '<=', self.date_to),
            ('pay_date', '>=', self.date_from),
            ('employee_id', '=', self.employee_id.id),
            ('is_validate_extra_hour', '=', True)
        ])
        he_25 = 0.0
        he_35 = 0.0
        r_he_25 = 0.0
        r_he_35 = 0.0
        he_100 = 0.0
        nightly_hours = 0.0
        if analytic_lines:
            he_25 = sum(line.extra_hour_25 for line in analytic_lines)
            he_35 = sum(line.extra_hour_35 for line in analytic_lines)
            r_he_25 = sum(line.r_extra_hour_25 for line in analytic_lines)
            r_he_35 = sum(line.r_extra_hour_35 for line in analytic_lines)
            nightly_hours = sum(line.night_hours for line in analytic_lines)
            he_100 = sum(line.hour_100 for line in analytic_lines)
        for line in self.worked_days_line_ids:
            if line.work_entry_type_id.code == 'WORKN':
                nightly_hours = nightly_hours + line.number_of_hours
        input_he_25 = self.env.ref('legal_benefits_rule.hr_payslip_input_type_he_025')
        input_hea_25 = self.env.ref('legal_benefits_rule.hr_payslip_input_type_hea_025')
        input_he_35 = self.env.ref('legal_benefits_rule.hr_payslip_input_type_he_035')
        input_r_he_35 = self.env.ref('legal_benefits_rule.hr_payslip_input_type_hea_035')
        input_he_100 = self.env.ref('legal_benefits_rule.hr_payslip_input_type_he_100')
        input_nightly_hours = self.env.ref('legal_benefits_rule.hr_payslip_input_type_hnt_001')
        for result in res:
            if result.get('code') == input_he_25.code:
                result['amount'] = he_25
            elif result.get('code') == input_he_35.code:
                result['amount'] = he_35
            elif result.get('code') == input_hea_25.code:
                result['amount'] = r_he_25
            elif result.get('code') == input_r_he_35.code:
                result['amount'] = r_he_35
            elif result.get('code') == input_he_100.code:
                result['amount'] = he_100
            elif result.get('code') == input_nightly_hours.code:
                result['amount'] = nightly_hours
        return res
