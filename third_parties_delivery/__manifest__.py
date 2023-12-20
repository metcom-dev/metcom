{
    'name': 'Third parties delivery',
    'version': '16.0.0.1.0',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    'summary': 'Add an additional field to indicate a delivery address to third parties in the delivery guide (Warehouse exit note).',
    'depends': [
        'stock',
        'l10n_pe_edi_stock_20',
        'l10n_pe_delivery_note_20'
    ],
    'data': [
        'data/edi_delivery_guide.xml',
        'views/stock_views.xml'],
    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'currency': 'USD',
    'price': 10.00
}
