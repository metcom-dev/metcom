{
    'name': 'Comisiones de AFP',
    'version': '16.0.0.0.0',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    'summary': 'Make the monthly search of the different types of percentage of the AFP',
    'description': '''
    It allows keeping updated the different types of AFP commissions and the maximum amount of afp for the calculation of the payroll.
    ''',
    'category': 'Payroll',
    'depends': ['account', 'types_system_pension'],
    'data': ['data/ir_cron.xml',
             'views/pension_system_view.xml',
             ],
    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'currency': 'USD',
    'price': 0.00
}
