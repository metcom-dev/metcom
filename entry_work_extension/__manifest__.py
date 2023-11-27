{
    'name': 'extensión trabajo entrada',
    'version': '16.0.1.0.1',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    'description': "Management of loans and salary advances to employees",
    'live_test_url': 'https://www.ganemo.co/demo',
    'category': 'Payroll',
    'depends': ['hr_payroll', 'hr_work_entry_contract'],
    'data': [
        'wizards/hr_work_entry_regeneration_wizard_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'currency': 'USD',
    'price': 0.00
}
