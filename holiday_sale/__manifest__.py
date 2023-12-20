{
    'name': 'Holiday Sale',
    'version': '16.0.0.0.3',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    'live_test_url': 'https://www.ganemo.co/demo',
    'description': "It allows to manage the process of sale-purchase vacations in odoo.",
    'summary': "It allows to manage the process of sale-purchase vacations in odoo.",
    'category': 'Payroll',
    'depends': [
        'hr_holidays',
        'legal_data',
        'hr_payroll',
        'voucher_lbs',
        'voucher_payroll',
        'basic_rule',
        'holiday_rule',
        'legal_benefits_rule',
        'rules_utilities',
        'payroll_utilities',
    ],
    'data': [
        'data/hr_work_entry_type_data.xml',
        'data/hr_leave_type_data.xml',
        'views/wizard_views.xml',
        'reports/holiday_sale_report.xml',
        'reports/holiday_sale_template.xml'
    ],
    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'currency': 'USD',
    'price': 0.00
}
