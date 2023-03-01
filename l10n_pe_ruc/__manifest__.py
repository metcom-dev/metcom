{
    "name": "Ruc Validation Conflux",
    'version': '16.0.0',
    'author': 'Conflux',
    'website': 'https://conflux.pe',
    'description': """
        Permite consulta RUC en base a DNI, pasaporte, Carnet de Extranjería y RUC desde los contactos de Odoo.
    """,
    'depends': [
        'base',
        'contacts',
    ],
    'data': [
        'views/partner_views.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'auto_install': False,
}
