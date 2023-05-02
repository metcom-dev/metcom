# -*- coding: utf-8 -*-
{
    'name' : 'Perzonalización de Ordenes de Compra',
    'version' : '16.0.1',
    'summary': 'Perzonalización de Ordenes de Compra MetCom',
    'sequence': 10,
    'description': """
        Perzonalización de Ordenes de Compra MetCom
    """,
    'category': 'Purchase',
    'license': 'OPL-1',
    'website': 'https://conflux.pe',
    'depends' : ['purchase'],
    'data': [
        "views/purchase_order_view.xml",
    ],
    'qweb': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}