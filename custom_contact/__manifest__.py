# -*- coding: utf-8 -*-
{
    'name' : 'Perzonalización de Contactos',
    'version' : '16.0.1',
    'summary': 'Personalización de Contactos MetCom',
    'sequence': 10,
    'description': """
        Personalizacion de Contactos MetCom
    """,
    'category': 'Stock',
    'license': 'LGPL-3',
    'website': 'https://conflux.pe',
    'depends' : ['base', 'account'],
    'data': [
        "views/res_partner_view.xml",
    ],
    'qweb': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}