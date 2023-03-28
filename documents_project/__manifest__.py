{
    'name': 'Files for Projects',
    'description': 'Este módulo lista los archivos por proyecto y almacen.',
    'category': 'Project Management',
    'version': '1.0',
    'author': 'Conflux',
    'depends': ['base', 'project', 'custom_project'],
    'data': [
        'views/files_view.xml',
        'security/ir.model.access.csv',
        'security/security.xml'
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
