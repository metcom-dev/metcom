{
    'name': 'Payroll utilites',
    'version': '16.0.0.0.0',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    'description': 'Allows you to manage the payment of benefits to employees',
    'depends': [
        'setting_rules_payroll',
        'hr_holidays',
        'payroll_fields',
        'absence_day',
        'hr_localization_menu'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/data_utilities_views.xml',
        'views/hr_views.xml'
    ],
    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'currency': 'USD',
    'price': 0.00
}
