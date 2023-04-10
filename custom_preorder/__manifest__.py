# -*- coding: utf-8 -*-
{
    'name' : 'Perzonalización de Pre-Ordenes de Compra',
    'version' : '16.0.1',
    'summary': 'Perzonalización de Pre-Ordenes de Compra MetCom',
    'sequence': 10,
    'description': """
        Perzonalización de Pre-Ordenes de Compra MetCom
    """,
    'category': 'Purchase',
    'license': 'OPL-1',
    'website': 'https://conflux.pe',
    'depends' : ['purchase_preorder', 'purchase_order_cron'],
    'data': [
        "views/purchase_preorder_view.xml",
    ],
    'qweb': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}