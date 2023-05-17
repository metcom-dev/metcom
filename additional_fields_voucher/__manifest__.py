{
    'name': 'Additional fields voucher',
    'version': '16.0.0.0.0',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    'description': """
Agrega campos al formato de boleta de pago
""",
    'depends': [
        'hr_payroll',
        'identification_type_employee'
    ],
    'data': ['views/hr_views.xml'],
    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'currency': 'USD',
    'price': 0.00
}
