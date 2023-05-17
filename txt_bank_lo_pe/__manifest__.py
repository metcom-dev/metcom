{
    'name': 'txt_bank_lo_pe',
    'version': '16.0.0.0.0',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    'live_test_url': 'https://www.ganemo.co/demo',
    'description': "this module allows to issue txt files for the payment of the payroll",
    'summary': 'this module allows to issue txt files for the payment of the payroll',
    'category': 'Payroll',
    'depends': [
        'hr_localization_menu',
        'type_bank_accounts',
        'hr_payroll',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_massive_payment_views.xml',
        'views/res_partner_bank_views.xml',
        'views/hr_payslip_net_others.xml',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'currency': 'USD',
    'price': 0.00
}
