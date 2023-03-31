{
    'name': 'Documentos para Proyectos',
    'description': 'Este módulo lista los archivos por proyecto y almacen.',
    'category': 'Project Management',
    'version' : '16.0.1',
    'author': 'Conflux',
    'license': 'OPL-1',
    'website': 'https://conflux.pe',
    'depends': [
        'base',
        'documents',
        'project',
        'custom_project',
    ],
    'data': [
        'views/project_documents_view.xml',
        'security/ir.model.access.csv',
        'security/security.xml'
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}