from odoo import api, SUPERUSER_ID


def _entry_change(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    section_lbs_1 = env.ref('voucher_lbs.section_lbs_1')  # Remuneración
    section_lbs_2 = env.ref('voucher_lbs.section_lbs_2')  # Vacaciones

    type_worked = env.ref('voucher_payroll.hr_work_entry_type_worked')  # Días Trabajados
    type_break = env.ref('voucher_payroll.hr_work_entry_type_break')  # Días descanso
    type_sanctioned = env.ref('voucher_payroll.hr_work_entry_type_sanctioned')  # Días Sanc.Disc
    type_not_working = env.ref('voucher_payroll.hr_work_entry_type_not_working')  # D.no lab / sub
    type_subsidies = env.ref('voucher_payroll.hr_work_entry_type_subsidies')  # Dias subsidios
    type_middle_rest = env.ref('voucher_payroll.hr_work_entry_type_middle_rest')  # Dias D.medicos
    type_holidays = env.ref('voucher_payroll.hr_work_entry_type_holidays')  # Días Vacaciones


    var_work_entry = env.ref('hr_work_entry.work_entry_type_attendance')
    var_work_entry.section_lbs_ids = section_lbs_1
    var_work_entry.type_inputs_ids = type_worked

    var_work_entry = env.ref('absence_day.hr_work_entry_type_ddo')
    var_work_entry.section_lbs_ids = section_lbs_1
    var_work_entry.type_inputs_ids = type_break

    var_work_entry = env.ref('absence_day.hr_work_entry_type_global')
    var_work_entry.section_lbs_ids = section_lbs_1
    var_work_entry.type_inputs_ids = type_break

    var_work_entry = env.ref('absence_day.hr_work_entry_type_workn')
    var_work_entry.section_lbs_ids = section_lbs_1
    var_work_entry.type_inputs_ids = type_worked

    var_hr_leave_type = env.ref('automatic_leave_type.hr_leave_type_01')
    var_work_entry = env.ref('automatic_leave_type.hr_work_entry_type_01')
    var_work_entry.section_lbs_ids = section_lbs_1
    var_work_entry.type_inputs_ids = type_sanctioned
    var_work_entry.leave_type_ids = [(4, var_hr_leave_type.id, 0)]

    var_hr_leave_type = env.ref('automatic_leave_type.hr_leave_type_02')
    var_work_entry = env.ref('automatic_leave_type.hr_work_entry_type_02')
    var_work_entry.section_lbs_ids = section_lbs_1
    var_work_entry.type_inputs_ids = type_not_working
    var_work_entry.leave_type_ids = [(4, var_hr_leave_type.id, 0)]

    var_hr_leave_type = env.ref('automatic_leave_type.hr_leave_type_03')
    var_work_entry = env.ref('automatic_leave_type.hr_work_entry_type_03')
    var_work_entry.section_lbs_ids = section_lbs_1
    var_work_entry.type_inputs_ids = type_not_working
    var_work_entry.leave_type_ids = [(4, var_hr_leave_type.id, 0)]

    var_hr_leave_type = env.ref('automatic_leave_type.hr_leave_type_04')
    var_work_entry = env.ref('automatic_leave_type.hr_work_entry_type_04')
    var_work_entry.section_lbs_ids = section_lbs_1
    var_work_entry.type_inputs_ids = type_not_working
    var_work_entry.leave_type_ids = [(4, var_hr_leave_type.id, 0)]

    var_hr_leave_type = env.ref('automatic_leave_type.hr_leave_type_05')
    var_work_entry = env.ref('automatic_leave_type.hr_work_entry_type_05')
    var_work_entry.section_lbs_ids = section_lbs_1
    var_work_entry.type_inputs_ids = type_not_working
    var_work_entry.leave_type_ids = [(4, var_hr_leave_type.id, 0)]

    var_hr_leave_type = env.ref('automatic_leave_type.hr_leave_type_06')
    var_work_entry = env.ref('automatic_leave_type.hr_work_entry_type_06')
    var_work_entry.section_lbs_ids = section_lbs_1
    var_work_entry.type_inputs_ids = type_not_working
    var_work_entry.leave_type_ids = [(4, var_hr_leave_type.id, 0)]

    var_hr_leave_type = env.ref('automatic_leave_type.hr_leave_type_07')
    var_work_entry = env.ref('automatic_leave_type.hr_work_entry_type_07')
    var_work_entry.section_lbs_ids = section_lbs_1
    var_work_entry.type_inputs_ids = type_not_working
    var_work_entry.leave_type_ids = [(4, var_hr_leave_type.id, 0)]

    var_hr_leave_type = env.ref('automatic_leave_type.hr_leave_type_08')
    var_work_entry = env.ref('automatic_leave_type.hr_work_entry_type_08')
    var_work_entry.section_lbs_ids = section_lbs_1
    var_work_entry.type_inputs_ids = type_not_working
    var_work_entry.leave_type_ids = [(4, var_hr_leave_type.id, 0)]

    var_hr_leave_type = env.ref('automatic_leave_type.hr_leave_type_09')
    var_work_entry = env.ref('automatic_leave_type.hr_work_entry_type_09')
    var_work_entry.section_lbs_ids = section_lbs_1
    var_work_entry.type_inputs_ids = type_subsidies
    var_work_entry.leave_type_ids = [(4, var_hr_leave_type.id, 0)]

    var_hr_leave_type = env.ref('automatic_leave_type.hr_leave_type_10')
    var_work_entry = env.ref('automatic_leave_type.hr_work_entry_type_10')
    var_work_entry.section_lbs_ids = section_lbs_1
    var_work_entry.type_inputs_ids = type_not_working
    var_work_entry.leave_type_ids = [(4, var_hr_leave_type.id, 0)]

    var_hr_leave_type = env.ref('automatic_leave_type.hr_leave_type_11')
    var_work_entry = env.ref('automatic_leave_type.hr_work_entry_type_11')
    var_work_entry.section_lbs_ids = section_lbs_1
    var_work_entry.type_inputs_ids = type_not_working
    var_work_entry.leave_type_ids = [(4, var_hr_leave_type.id, 0)]

    var_hr_leave_type = env.ref('automatic_leave_type.hr_leave_type_12')
    var_work_entry = env.ref('automatic_leave_type.hr_work_entry_type_12')
    var_work_entry.section_lbs_ids = section_lbs_1
    var_work_entry.type_inputs_ids = type_not_working
    var_work_entry.leave_type_ids = [(4, var_hr_leave_type.id, 0)]

    var_hr_leave_type = env.ref('automatic_leave_type.hr_leave_type_20')
    var_work_entry = env.ref('automatic_leave_type.hr_work_entry_type_20')
    var_work_entry.section_lbs_ids = section_lbs_1
    var_work_entry.type_inputs_ids = type_middle_rest
    var_work_entry.leave_type_ids = [(4, var_hr_leave_type.id, 0)]

    var_hr_leave_type = env.ref('automatic_leave_type.hr_leave_type_21')
    var_work_entry = env.ref('automatic_leave_type.hr_work_entry_type_21')
    var_work_entry.section_lbs_ids = section_lbs_1
    var_work_entry.type_inputs_ids = type_subsidies
    var_work_entry.leave_type_ids = [(4, var_hr_leave_type.id, 0)]

    var_hr_leave_type = env.ref('automatic_leave_type.hr_leave_type_22')
    var_work_entry = env.ref('automatic_leave_type.hr_work_entry_type_22')
    var_work_entry.section_lbs_ids = section_lbs_1
    var_work_entry.type_inputs_ids = type_subsidies
    var_work_entry.leave_type_ids = [(4, var_hr_leave_type.id, 0)]

    var_hr_leave_type = env.ref('automatic_leave_type.hr_leave_type_24')
    var_work_entry = env.ref('automatic_leave_type.hr_work_entry_type_24')
    var_work_entry.section_lbs_ids = section_lbs_1
    var_work_entry.type_inputs_ids = type_not_working
    var_work_entry.leave_type_ids = [(4, var_hr_leave_type.id, 0)]

    var_hr_leave_type = env.ref('automatic_leave_type.hr_leave_type_25')
    var_work_entry = env.ref('automatic_leave_type.hr_work_entry_type_25')
    var_work_entry.section_lbs_ids = section_lbs_1
    var_work_entry.type_inputs_ids = type_not_working
    var_work_entry.leave_type_ids = [(4, var_hr_leave_type.id, 0)]

    var_hr_leave_type = env.ref('automatic_leave_type.hr_leave_type_26')
    var_work_entry = env.ref('automatic_leave_type.hr_work_entry_type_26')
    var_work_entry.section_lbs_ids = section_lbs_1
    var_work_entry.type_inputs_ids = type_not_working
    var_work_entry.leave_type_ids = [(4, var_hr_leave_type.id, 0)]

    var_hr_leave_type = env.ref('automatic_leave_type.hr_leave_type_27')
    var_work_entry = env.ref('automatic_leave_type.hr_work_entry_type_27')
    var_work_entry.section_lbs_ids = section_lbs_1
    var_work_entry.type_inputs_ids = type_not_working
    var_work_entry.leave_type_ids = [(4, var_hr_leave_type.id, 0)]

    var_hr_leave_type = env.ref('automatic_leave_type.hr_leave_type_28')
    var_work_entry = env.ref('automatic_leave_type.hr_work_entry_type_28')
    var_work_entry.section_lbs_ids = section_lbs_1
    var_work_entry.type_inputs_ids = type_not_working
    var_work_entry.leave_type_ids = [(4, var_hr_leave_type.id, 0)]

    var_hr_leave_type = env.ref('automatic_leave_type.hr_leave_type_29')
    var_work_entry = env.ref('automatic_leave_type.hr_work_entry_type_29')
    var_work_entry.section_lbs_ids = section_lbs_1
    var_work_entry.type_inputs_ids = type_not_working
    var_work_entry.leave_type_ids = [(4, var_hr_leave_type.id, 0)]

    var_hr_leave_type = env.ref('automatic_leave_type.hr_leave_type_30')
    var_work_entry = env.ref('automatic_leave_type.hr_work_entry_type_30')
    var_work_entry.section_lbs_ids = section_lbs_1
    var_work_entry.type_inputs_ids = type_not_working
    var_work_entry.leave_type_ids = [(4, var_hr_leave_type.id, 0)]

    var_hr_leave_type = env.ref('automatic_leave_type.hr_leave_type_31')
    var_work_entry = env.ref('automatic_leave_type.hr_work_entry_type_31')
    var_work_entry.section_lbs_ids = section_lbs_1
    var_work_entry.type_inputs_ids = type_not_working
    var_work_entry.leave_type_ids = [(4, var_hr_leave_type.id, 0)]

    var_hr_leave_type = env.ref('automatic_leave_type.hr_leave_type_32')
    var_work_entry = env.ref('automatic_leave_type.hr_work_entry_type_32')
    var_work_entry.section_lbs_ids = section_lbs_1
    var_work_entry.type_inputs_ids = type_not_working
    var_work_entry.leave_type_ids = [(4, var_hr_leave_type.id, 0)]

    var_hr_leave_type = env.ref('automatic_leave_type.hr_leave_type_33')
    var_work_entry = env.ref('automatic_leave_type.hr_work_entry_type_33')
    var_work_entry.section_lbs_ids = section_lbs_1
    var_work_entry.type_inputs_ids = type_not_working
    var_work_entry.leave_type_ids = [(4, var_hr_leave_type.id, 0)]

    var_hr_leave_type = env.ref('automatic_leave_type.hr_leave_type_34')
    var_work_entry = env.ref('automatic_leave_type.hr_work_entry_type_34')
    var_work_entry.section_lbs_ids = section_lbs_1
    var_work_entry.type_inputs_ids = type_not_working
    var_work_entry.leave_type_ids = [(4, var_hr_leave_type.id, 0)]

    var_hr_leave_type = env.ref('automatic_leave_type.hr_leave_type_35')
    var_work_entry = env.ref('automatic_leave_type.hr_work_entry_type_35')
    var_work_entry.section_lbs_ids = section_lbs_1
    var_work_entry.type_inputs_ids = type_not_working
    var_work_entry.leave_type_ids = [(4, var_hr_leave_type.id, 0)]

    var_hr_leave_type = env.ref('holiday_process.hr_leave_type_23')
    var_work_entry = env.ref('holiday_process.hr_work_entry_type_23')
    var_work_entry.section_lbs_ids = section_lbs_2
    var_work_entry.type_inputs_ids = type_holidays
    var_work_entry.leave_type_ids = [(4, var_hr_leave_type.id, 0)]
