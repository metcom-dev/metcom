from odoo import models, fields, api
from datetime import datetime


class ReportVoucherLbs(models.AbstractModel):
    _name = 'report.voucher_lbs.report_payslip_voucher_lbs'
    _description = 'Voucher Lbs'

    @api.model
    def _get_report_values(self, docids=None, data=None):
        payslips = self.env['hr.payslip'].browse(docids)
        return {
            'doc_ids': docids,
            'docs': payslips,
            'data': data,
            'employer_sign': self.env['hr.employee'].get_employer_sign(),
            'lbs_lines': self._get_lbs_lines(payslips),
            'lbs_total_values': self.get_lbs_total_values(payslips)
        }

    def get_lbs_total_values(self, payslips):
        lines = {}
        parent_net = self.env.ref('hr_payroll.NET', False)
        parent_net += self.env['hr.salary.rule.category'].search([('parent_id', '=', parent_net.id)])
        parent_ing_001 = self.env.ref('basic_rule.hr_salary_rule_category_ing_001', False)
        parent_ing_001 += self.env['hr.salary.rule.category'].search([('parent_id', '=', parent_ing_001.id)])

        for payslip in payslips:
            net_lines = payslip.line_ids.filtered(lambda x: x.category_id in parent_ing_001)
            net_amount = sum(line.total for line in net_lines)
            ded_lines = payslip.line_ids.filtered(lambda x: x.category_id.code == 'DAT_001')
            ded_amount = sum(line.total for line in ded_lines)
            net_003_lines = payslip.line_ids.filtered(lambda x: x.category_id in parent_net)
            net_003_amount = sum(line.total for line in net_003_lines)
            dae_001_lines = payslip.line_ids.filtered(lambda x: x.category_id.code == 'DAE_001')
            lines.update({payslip.id: {
                'net_amount': float('%.2f' % net_amount),
                'ded_amount': float('%.2f' % ded_amount),
                'net_003_amount': float('%.2f' % net_003_amount),
                'dae_001_lines': dae_001_lines
            }})
        return lines

    def _get_lbs_lines(self, payslips):
        lines = {}
        section_lbs_ids = self.env['section.lbs'].search([], order='code asc')
        for payslip in payslips:
            lines.update({payslip.id: {
                'lbs_lines': self.get_lbs_merge_lines(payslip, section_lbs_ids),
                'section_lbs_ids': section_lbs_ids
            }})
        return lines

    def get_worked_days_period(self, payslip, section_code, work_day_code):
        date_from = False
        date_to = False
        if section_code in ['1', '5', '6', '7']:
            date_from = payslip.date_from.strftime('%d/%m/%Y')
            date_to = payslip.date_to.strftime('%d/%m/%Y')
        elif section_code == '2':
            if work_day_code == 'VAC_LBS':
                hr_allocation_ids = []
                employee_id = payslip.employee_id
                if employee_id and employee_id.service_termination_date:
                    leave_23 = self.env.ref('holiday_process.hr_leave_type_23')
                    hr_leave_ids = self.env['hr.leave'].search([
                        ('holiday_status_id', '=', leave_23.id),
                        ('employee_id', '=', employee_id.id),
                        ('request_date_from', '<=', employee_id.service_termination_date),
                        ('request_date_to', '>=', employee_id.service_termination_date),
                        ('state', 'in', ['validate1', 'validate']),
                    ])
                    for hr_leave in hr_leave_ids:
                        allocation = hr_leave.hr_leave_id
                        if allocation:
                            hr_allocation_ids.append(allocation)
            else:
                hr_allocation_ids = payslip.hr_allocation_ids.filtered(lambda x: x.holiday_status_id.code == work_day_code)
            period_format = ''
            for allocation in hr_allocation_ids:
                date_from = allocation.date_from.strftime('%d/%m/%Y')
                date_to = allocation.date_to.strftime('%d/%m/%Y')
                if period_format != '':
                    period_format = '<br/>'
                period_format += '{} AL {}'.format(date_from, date_to)
            return period_format
        elif section_code in ['3', '4']:
            if work_day_code not in ['MES_002', 'MES_003', 'DIAS_003']:
                return ''
            payslip_line = self.env['hr.payslip.line']
            date_start, year, month, _ = payslip.generate_date_start_month_year(payslip.date_from, payslip.date_to)
            month = int(month)
            year = int(year)

            start_m, star_y = payslip_line._get_month(year, month, 6)
            end_m, end_y = payslip_line._get_month(year, month, 1)
            periods = payslip_line._get_periods(start_m, star_y, end_m, end_y)

            if section_code == '3':
                if work_day_code == 'MES_002':
                    date_from, date_to = self._get_calc_cts_grat_per_days(periods, payslip.contract_id, date_start, month, 'CTS_002')
                else:
                    return self._get_calc_dias_003(payslip, periods, date_from, date_to, date_start)

            else:
                date_from, date_to = self._get_calc_cts_grat_per_days(periods, payslip.contract_id, date_start, month, 'GRAT_001')
        if date_from and date_to:
            return '{} AL {}'.format(date_from, date_to)
        return ''

    def _get_calc_dias_003(self, payslip, periods, date_from, date_to, date_start):
        service_start_date = payslip.employee_id.service_start_date
        service_termination_date = payslip.employee_id.service_termination_date
        worked_lines = self.env['hr.payslip.worked_days'].search([
            ('date_start', 'in', periods),
            ('employee_id', '=', payslip.employee_id.id),
            ('number_of_days', '>', 0)
        ])
        service_date = '{}/{}'.format(service_start_date.strftime('%m'), service_start_date.strftime('%Y'))
        filter_dias_003 = worked_lines.filtered(lambda x: x.date_start == service_date)
        day_service_start_date = int(service_start_date.strftime('%d'))
        if filter_dias_003 and day_service_start_date > 1:
            date_from = service_start_date.strftime('%d/%m/%Y')
            first_day, last_day = self.env['hr.payslip'].get_month_day_range(service_date)
            date_to = last_day.strftime('%d/%m/%Y')
        if service_termination_date:
            worked_lines += self.env['hr.payslip.worked_days'].search([
                ('date_start', '=', date_start),
                ('employee_id', '=', payslip.employee_id.id),
                ('number_of_days', '>', 0)
            ])
            termination_date = '{}/{}'.format(service_termination_date.strftime('%m'), service_termination_date.strftime('%Y'))
            if service_termination_date and termination_date != service_date:
                filter_dias_003 = worked_lines.filtered(lambda x: x.date_start == termination_date)
                day_service_termination_date = int(service_termination_date.strftime('%d'))
                if filter_dias_003 and day_service_termination_date < 30:
                    month = service_termination_date.strftime('%m')
                    year = service_termination_date.strftime('%Y')
                    first_day = '{}-{}-01 07:00:00'.format(year, month)
                    if not date_from:
                        date_from = datetime.strptime(first_day, '%Y-%m-%d %H:%M:%S').date().strftime('%d/%m/%Y')
                        date_to = service_termination_date.strftime('%d/%m/%Y')
                    else:
                        data = '{} AL {}'.format(date_from, date_to)
                        date_from = datetime.strptime(first_day, '%Y-%m-%d %H:%M:%S').date().strftime('%d/%m/%Y')
                        date_to = service_termination_date.strftime('%d/%m/%Y')
                        data += '<br/>{} AL {}'.format(date_from, date_to)
                        return data
        if date_from and date_to:
            return '{} AL {}'.format(date_from, date_to)
        return ''

    def _get_calc_cts_grat_per_days(self, periods, contract_id, date_start, month, code):
        periods.append(date_start)

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
        service_date_t = '{}/{}'.format(service_termination_date.strftime('%m'), service_termination_date.strftime('%Y')) if service_termination_date else False

        for period in periods:
            if slip_line_ids and period == slip_line_ids.date_start and period[0:2] in ['12', '07']:
                break
            else:
                new_periods.append(period)

        if service_start_day != '01':
            new_periods = list(filter(lambda d: d != service_date_s, new_periods))
        if service_termination_date and date_start == service_date_t and service_termination_day < 31 and month != 12:
            new_periods = list(filter(lambda d: d != service_date_t, new_periods))

        date_from = False
        date_to = False

        if new_periods:
            new_periods = self.env['hr.payslip'].get_order_periods(new_periods)
            len_periods = len(new_periods)
            date_from = '01/{}'.format(new_periods[0])
            tmp_period = '{}/{}'.format(new_periods[len_periods - 1][0:2], new_periods[len_periods - 1][3:])
            first_day, last_day = self.env['hr.payslip'].get_month_day_range(tmp_period)
            date_to = last_day.strftime('%d/%m/%Y')
        return date_from, date_to

    def get_lbs_merge_lines(self, payslip, section_lbs_ids):
        work_day_section = payslip.worked_days_line_ids.mapped('work_entry_type_id')
        data = {}
        for section in section_lbs_ids:
            work_day = work_day_section.filtered(lambda x: x.section_lbs_ids.filtered(lambda y: section.code == y.code))
            salary_rule = payslip.line_ids.filtered(lambda x: x.salary_rule_id.section_lbs_ids.filtered(lambda y: section.code == y.code))
            if work_day:
                filter_work_days_codes = work_day.mapped('code')
                work_day_data = payslip.worked_days_line_ids.filtered(lambda x: x.code in filter_work_days_codes)
                work_day_data = sorted(work_day_data, key=lambda x: x.code)
                data = self.update_dict_lines_lbs(payslip, work_day_data, data, section, 1) if work_day_data else data
            if salary_rule:
                salary_rule = sorted(salary_rule, key=lambda x: x.sequence)
                data = self.update_dict_lines_lbs(payslip, salary_rule, data, section, 2) if salary_rule else data
        return data

    def update_dict_lines_lbs(self, payslip, lines, data, section, position):
        for line in lines:
            value = line.total if line._name == 'hr.payslip.line' else line.number_of_days
            if value <= 0:
                continue
            new_values = [{
                'name': line.name,
                'value': value,
                'value_2': 0,
                'period': self.get_worked_days_period(payslip, section.code, line.code),
                'position': position
            }]
            if line._name != 'hr.payslip.line':
                dict_values = {}
                if section.code in ['1', '2'] or (section.code == '3' and line.code == 'DIAS_003'):
                    dict_values = {
                        'value': 0,
                        'value_2': value
                    }
                elif section.code in ['3', '4'] and line.code in ['MES_002', 'MES_003']:
                    dict_values = {
                        'value': int(value / 30)
                    }
                new_values[0].update(dict_values)

            if data.get(section.code):
                data[section.code] += new_values
            else:
                data.setdefault(section.code, new_values)
        return data
