# -*- coding: utf-8 -*-
{
    'name' : 'Crons Personalizados - Orden de Compra',
    'version' : '16.0.1',
    'summary': 'Crons Personalizados MetCom',
    'sequence': 10,
    'description': """
        Crons Personalizados para MetCom
    """,
    'category': 'Purchase',
    'license': 'OPL-1',
    'website': 'https://conflux.pe',
    'depends' : ['purchase', 'purchase_preorder'],
    'data': [
        "data/ir_cron.xml",
        "reports/purchase_quotation_template.xml",
        "reports/purchase_order_template.xml",
    ],
    'qweb': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}