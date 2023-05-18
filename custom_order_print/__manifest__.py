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
        'security/security.xml',
        "views/purchase_order.xml",
        "views/purchase_order_template_inherit.xml"
    ],
    'assets': {
        'web.report_assets_common': [
            'custom_order_print/static/src/scss/custom_styles.scss',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}