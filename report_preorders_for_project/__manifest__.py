{
    'name': "Reporte de pre-ordenes por proyecto",
    'license': "OPL-1",
    'version': '16.0.0',
    'website': "https://conflux.pe",
    'category': "Tools",
    'depends': ['purchase_preorder', 'project'],
    'data': [
		'security/ir.model.access.csv',
        'wizard/preorder_project_view.xml',
    ],
    'application': True,
    'installable': True,
}