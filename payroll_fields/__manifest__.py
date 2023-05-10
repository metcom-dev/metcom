{
    "name": "Payroll fields",
    'version': '16.0.0.0.0',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    "description": """
Este modulo crea un campo mes de nómina el cual controla a que mes corresponde cada nómina, adicional crea el menú 
de analisis días, entradas, y planilla para un mejor control de importar información y analisis de nóminas.
    """,
    "depends": [
        'additional_fields_employee',
        'hr_payroll'],
    "data": [
        'security/hr_rules.xml',
        'views/hr_payslip_views.xml',
        'views/hr_payslip_input_views.xml',
        'views/hr_payslip_line_views.xml',
        'views/hr_payslip_worked_days_views.xml'
    ],
    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'currency': 'USD',
    'price': 0.00
}
