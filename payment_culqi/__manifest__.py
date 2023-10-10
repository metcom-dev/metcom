{
    'name': 'Culqi Payment Acquirer',
    'version': '16.0.0.0.0',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    'summary': 'Payment Acquirer: Culqi Implementation',
    'category': 'eCommerce',
    'depends': ['payment'],
    'data': [
        'views/payment_provider_views.xml',
        'views/templates.xml',
        
        'data/payment_provider_data.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'payment_culqi/static/src/js/card_lib.js',
            'payment_culqi/static/src/js/culqi_form.js',
            'payment_culqi/static/src/css/culqi.css',
        ],
    },
    'application': False,
    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
    'currency': 'USD',
    'price': 99.99
}