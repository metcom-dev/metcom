{
    'name': "Reporte Registro de ventas y Registro de compras",
    'version': '16.0.0',
    'author': 'Conflux',
    'website': "https://conflux.pe",
    'category': 'Account',
    'version': '0.1',
    'license': 'LGPL-3',
    'depends': [
        # 'l10n_pe_edi_extended',
        # 'company_branch_address_account',
        'l10n_latam_invoice_document',
        'report_xlsx'
    ],
    'data': [
        'security/ir.model.access.csv',
        'wizards/account_sale_record.xml',
        'wizards/account_purchase_record.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}