{
    'name': 'Formato 3.20 Libro de Inventarios y Balances - Estado de resultados (Enterprise)',
    'version': '16.0.0.0.1',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    'summary': 'This module creates the format 3.20 "Statement of income" of the electronic inventory and balance book (Enterprise).',
    'description': 'This module creates the format 3.20 "Statement of income" of the electronic inventory and balance book (Enterprise).',
    'category': 'Accounting',
    'depends': [
        'account_reports',
        'ple_inv_and_bal_0301'
    ],

    'data': [
        'security/ir.model.access.csv',
        'reports/ple_inv_bal_report.xml',
        'reports/print_template.xml',       
        'views/ple_inv_bal_views_20.xml',
        'views/wizard_report_view.xml',        
    ],
    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'currency': 'USD',
    'price': 50.00
}
