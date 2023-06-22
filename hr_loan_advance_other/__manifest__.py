{
    'name': 'HR - loan advance other',
    'version': '16.0.0.0.0',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    'summary': 'Gestion de prestamos y adelantos de sueldo a empleados',
    'description': """Gestion de prestamos y adelantos de sueldo a empleados""",
    'category': 'Payroll',
    'depends': [
        'account',
        'hr_payroll',
        'automatic_functions_rule',
        'payment_conditions'
    ],
    'data': [
        'data/hr_data.xml',
        'data/ir_sequence_data.xml',
        'security/ir.model.access.csv',
        'security/ir_rule.xml',
        'views/hr_loan_views.xml',
        'views/hr_other_discounts_views.xml',
        'views/hr_salary_advance_views.xml',
        'views/hr_views.xml',
        'wizards/payment_anticipated_loan_view.xml'
    ],
    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'currency': 'USD',
    'price': 0.00
}
