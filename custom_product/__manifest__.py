# -*- coding: utf-8 -*-
{
    'name' : 'Perzonalización de Productos',
    'version' : '16.0.1',
    'summary': 'Personalización de Productos MetCom',
    'sequence': 10,
    'description': """
        Personalizacion de Productos MetCom
    """,
    'category': 'Stock',
    'license': 'LGPL-3',
    'website': 'https://conflux.pe',
    'depends' : ['stock'],
    'data': [
        "views/product_category_view.xml",
    ],
    'qweb': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}