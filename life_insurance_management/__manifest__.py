{
    'name': 'Life insurance management',
    'version': '16.0.1.1.3',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    'category': 'Payroll',
    'summary': 'Este módulo permite gestionar las poliza de seguro de vida.',
    'description': """
    Este módulo permite gestionar las poliza de seguro de vida.
    """,
    'depends': [
        'localization_menu',
        'hr',
        'eps_process'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_views.xml',
        'views/life_insurance_views.xml'
    ],
    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'currency': 'USD',
    'price': 0.0
}
