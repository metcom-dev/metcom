{
    'name': "Pre-orden de compra",
    'author': "Conflux",
    'license': "AGPL-3",
    'version': '16.0.0',
    'website': "https://conflux.pe",
    'category': "Tools",
    'depends': ['base', 'contacts', 'mail', 'purchase', 'stock'],
    'data': [
		'security/security.xml',
		'security/ir.model.access.csv',
        'report/report_purchase_preorder.xml',
        'data/ir_sequence.xml',
        'data/mail_template.xml',
        'views/purchase_preorder_views.xml',
    ],
    'application': True,
    'installable': True,
}