{
    'name': 'Conciliation payroll',
    'version': '16.0.0.1.0',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    'description': "",
    'depends': [
        'hr_payroll_account',
        'txt_bank_lo_pe',
    ],
    'data': [
        'views/hr_massive_payment_views.xml',
        'views/hr_payslip_views.xml'
    ],
    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'currency': 'USD',
    'price': 0.00
}
