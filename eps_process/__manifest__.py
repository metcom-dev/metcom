{
    'name': 'employee eps management',
    'version': '16.0.1.0.2',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    'description': "This module allows you to manage the hiring process and eps control",
    'live_test_url': 'https://www.ganemo.co/demo',
    'category': 'Payroll',
    'depends': [
        'hr_payroll',
        'localization_menu',
        'additional_fields_employee',
        'personal_information',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/eps_credit_calculation.xml',
        'views/eps_management.xml',
        'views/eps_employee_relative.xml',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'currency': 'USD',
    'price': 0.00
}
