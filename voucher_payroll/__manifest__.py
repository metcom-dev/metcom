{
    'name': 'Voucher payroll',
    'version': '16.0.0.0.2',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    'live_test_url': 'https://www.ganemo.co/demo',
    'category': 'Payroll',
    'summary': 'This module issues the regular pay slip of the employees without overtime',
    'depends': [
        'employee_service',
        'absence_day',
        'filter_payroll',
        'additional_fields_voucher',
        'holiday_field_payroll',
        'payment_conditions',
        'types_system_pension'
    ],
    'data': [
        'data/hr_work_entry_type_data_ballots.xml',
        'security/ir.model.access.csv',
        'views/hr_views.xml',
        'views/reports.xml'
    ],
    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'currency': 'USD',
    'price': 0.0
}
