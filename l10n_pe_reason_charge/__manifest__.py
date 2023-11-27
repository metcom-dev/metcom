{
    'name': 'fields reason and charge for invoice',
    'version': '16.0.0.0.0',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    'summary': 'This module will validate the status of the invoice through the integrated query.',
    'category': 'Accounting',
    "depends": [
                'l10n_pe_edi',
                'classic_format_invoice'
                ],
    'data': [
        'views/l10n_pe_reason_charge_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'currency': 'USD',
    'price': 0.00
}
