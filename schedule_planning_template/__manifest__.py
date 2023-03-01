# -*- coding: utf-8 -*-
{
    'name' : 'Plantillas de Planificación de Horarios',
    'version' : '16.0.1',
    'summary': 'Personalización de Plantillas de Planificación de Horarios',
    'sequence': 10,
    'description': """
        Personalización de Plantillas de Planificación de Horarios
    """,
    'category': 'Planning',
    'license': 'OPL-1',
    'website': 'https://conflux.pe',
    'depends' : ['planning'],
    'data': [
        'security/ir.model.access.csv',
        "views/schedule_planning_template_view.xml",
    ],
    'qweb': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}