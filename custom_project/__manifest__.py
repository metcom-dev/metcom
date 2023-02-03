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
    'license': 'LGPL-3',
    'website': 'https://conflux.pe',
    'depends' : ['project'],
    'data': [
        'security/ir.model.access.csv',
        "views/project_view.xml",
    ],
    'qweb': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}