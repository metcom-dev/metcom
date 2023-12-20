{
    'name': 'l10n pe fields for classic format invoice',
    'version': '16.0.2.3.3',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    'summary': 'This module will be used to make the classic invoice compatible for the Peruvian localization.',
    'category': 'All',
    "depends": ['account',
                'l10n_pe',
                'l10n_pe_edi',
                'classic_format_invoice',
                'qr_code_on_sale_invoice',
                'account_exchange_currency'
    ],
    'data': [
        'data/2.1/edi_templates.xml',
        'views/classic_format_template.xml',
        'views/account_move.xml',
        'views/account_inherit.xml',
    ],
    'installable': True,
    'auto_install': False,
    'uninstall_hook': '_refactor_xml',
    'license': 'Other proprietary',
    'currency': 'USD',
    'price': 0.00
}
