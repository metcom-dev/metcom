{
    'name': 'Reporte Ventas detalladas',
    'version': '16.0.0',
    'category': 'Account',
    'author': 'Conflux',
    'sequence': 10,
    'description': "",
    'depends': [
        # 'company_branch_address_account',
        'report_xlsx'
    ],
    'data': [
        'security/ir.model.access.csv',
        'wizard/invoiced_sales_detail.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'OPL-1',
}