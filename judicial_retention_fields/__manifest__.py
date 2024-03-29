{
    'name': 'Judicial retention fields',
    'version': '16.0.0.0.0',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    'description': """
Agrega la sección en empleados donde se determina si el trabajador tiene un proceso Judicial de alimentación y 
se le debe registrar algún descuento.
    """,
    'depends': [
        'hr',
        'payment_conditions'
    ],
    'data': [
        'views/report.xml',
        'views/hr_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'currency': 'USD',
    'price': 0.0
}
