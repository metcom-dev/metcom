{
    'name': 'Control stock status of serial products',
    'version': '16.0.0.0.0',
    'author': 'Ganemo',
    'live_test_url': 'https://www.ganemo.co/demo',
    'website': 'https://www.ganemo.co',
    'summary': 'Controls stock status of products with series, identifying the status each time the product is moved.',
    'category': 'Inventory/Inventory',
    'depends': [
        'stock',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'currency': 'USD',
    'price': 99.00
}
