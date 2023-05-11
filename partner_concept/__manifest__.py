{
    'name': 'Partner Concept',
    'version': '16.0.0.0.0',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    'summary': "This module allows you to manage salary concepts individually for employees.",
    'description': """
    Generate the plame files for the declaration of the PDT Plame to sunat
    """,
    'depends': ['hr', 'hr_payroll'],
    'data': [
        'security/ir.model.access.csv',
        'views/partner_concept.xml'
    ],
    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'currency': 'USD',
    'price': 0.00
}
