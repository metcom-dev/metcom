{
    'name': 'Payment Conditions',
    'version': '16.0.0.0.0',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    'summary': 'Este módulo crea campos de periodicidad en el contrato y en la estructura.',
    'description': """
    Este módulo crea campos de periodicidad en el contrato y en la estructura.
    """,
    'depends': [
        'localization_menu',
        'hr_payroll'
    ],
    'data': [
        'data/data.xml',
        'security/ir.model.access.csv',
        'views/hr_views.xml',
        'views/payment_period_views.xml',
        'views/payment_type_views.xml',
        'views/special_situation_views.xml',
        'views/variable_payment_views.xml'
    ],
    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'currency': 'USD',
    'price': 0.0
}
