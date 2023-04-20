# -*- coding: utf-8 -*-
{
    'name' : 'Perzonalización de Impresión de Ordenes de Compra',
    'version' : '16.0.1',
    'summary': 'Perzonalización de Impresión de Ordenes de Compra MetCom',
    'sequence': 10,
    'description': """
        Perzonalización de Impreción de Ordenes de Compra MetCom
    """,
    'category': 'Purchase',
    'license': 'OPL-1',
    'website': 'https://conflux.pe',
    'depends' : ['purchase', 'custom_contact'],
    'data': [
        #
        "views/purchase_order.xml",
        "views/purchase_order_template_inherit.xml"
    ],
    'qweb': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}