{
    'name': 'payment term lines extension',
    'version': '16.0.0.0.3',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    'live_test_url': 'https://www.ganemo.co/demo',
    'description': 'Extend the module so that it rounds the lines of the payment terms and can change the accounting account of some line in the payment terms',
    'summary': 'Extend the module so that it rounds the lines of the payment terms and can change the accounting account of some line in the payment terms.',
    'depends': [
        'payment_term_lines',
        'automatic_account_change',
    ],
    'data': [
        'views/payment_line_view.xml',
    ],
    'category': 'All',
    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'currency': 'USD',
    'price': 8.00,
    'category': 'Accounting',
}

