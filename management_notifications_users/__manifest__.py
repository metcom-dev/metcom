{
    'name' : 'Gestion de Notificaciones al Correo Electronico',
    'version' : '16.0.1',
    'summary': 'Gestion de Notificaciones al Correo Electronico',
    'sequence': 10,
    'description': """
        Gestion de Notificaciones al Correo Electronico MetCom
    """,
    'license': 'OPL-1',
    'website': 'https://conflux.pe',
    'depends' : ['mail', 'project', 'purchase', 'purchase_preorder', 'stock', 'contacts', 'account_accountant'],
    'data': [
        'security/ir.model.access.csv',
        'views/management_user_view.xml',
    ],
    'qweb': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}