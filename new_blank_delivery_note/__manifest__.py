{
    'name': 'Blank delivery note format',
    'version': '16.0.0.0.0',
    'author': 'Ganemo, Tiam-V',
    'website': 'https://www.ganemo.co',
    'summary': 'Adds reference guide format where it only prints dynamic information and the layout is blank.',
    'category': 'Localization',
    'depends': [
        'account',
        'l10n_pe_edi_stock_20',
        'l10n_pe_delivery_note_ple',
        'third_parties_delivery'
    ],
    'data': [
        'reports/blank_delivery_note_template.xml',
        'reports/blank_delivery_report.xml',
    ],
    "assets": {
        "web.report_assets_common": [
            "new_blank_delivery_note/static/src/css/style_delivery_note.css",
        ],
    },
    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'currency': 'USD',
    'price': 400.00
}
