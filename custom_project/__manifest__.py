# -*- coding: utf-8 -*-
{
    'name' : 'Perzonalización de Proyectos',
    'version' : '16.0.1',
    'summary': 'Personalización de Proyectos MetCom',
    'sequence': 10,
    'description': """
        Personalizacion de Proyectos MetCom
    """,
    'category': 'Project',
    'license': 'OPL-1',
    'website': 'https://conflux.pe',
    'depends' : ['documents', 'project', 'purchase_preorder', 'sale_timesheet'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/ir_sequence.xml',
        "views/project_view.xml",
        "views/purchase_preorder_view.xml",
        "views/res_users_view.xml",
        "reports/report_purchase_preorder.xml",
    ],
    'qweb': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}