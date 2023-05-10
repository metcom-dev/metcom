{
    'name': 'Additional fields payroll',
    'version': '16.0.0.0.0',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    'description': "This module allows the allocation of the employee's pension system",
    'depends': [
        'localization_menu',
        'hr_payroll'
    ],
    'data': [
        'data/low_reason_data.xml',
        'security/ir.model.access.csv',
        'views/hr_views.xml',
        'views/low_reason_views.xml',
        'views/mintra_contract_views.xml'
    ],
    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'currency': 'USD',
    'price': 0.00
}
