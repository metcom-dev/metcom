{
    'name': 'Account field to force exchange rate',
    'version': '16.0.0.0.2',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    'summary': 'This module will create a field to force the exchange rate',
    'category': 'Accounting',
    'depends': [
        'account_exchange_currency',
        'payment_term_lines'
    ],
    'data': [
        'views/account_views.xml',
        'views/account_payment.xml',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'currency': 'USD',
    'price': 100.00
}
