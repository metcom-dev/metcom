# -*- coding: utf-8 -*-
{
    'name' : 'Crons Personalizados',
    'version' : '16.0.1',
    'summary': 'Crons Personalizados MetCom',
    'sequence': 10,
    'description': """
        Crons Personalizados para MetCom
    """,
    'category': 'Purchase',
    'license': 'LGPL-3',
    'website': 'https://conflux.pe',
    'depends' : ['purchase', 'purchase_preorder'],
    'data': [
        "data/ir_cron.xml",
    ],
    'qweb': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}