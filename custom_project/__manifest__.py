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
    'depends' : ['project', 'purchase_preorder'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/ir_sequence.xml',
        "views/project_view.xml",
        "views/purchase_preorder_view.xml",
        "views/res_users_view.xml"
    ],
    'qweb': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}