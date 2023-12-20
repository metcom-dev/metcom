{
    'name': 'Various data',
    'version': '16.0.0.2.6',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    'description': """
    Creates the tax data menu in location, where the models of Minimum Vital Remuneration, UIT, SIS, SCTR are created
    """,
    'depends': ['localization_menu',
                'hr',
                'types_system_pension',
                'eps_process'],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_views.xml',
        'views/various_data_rmv_views.xml',
        'views/various_data_sctr_views.xml',
        'views/various_data_sis_views.xml',
        'views/various_data_uit_views.xml'
    ],
    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'currency': 'USD',
    'price': 0.0
}
