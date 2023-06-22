{
    'name': 'Personal Information',
    'version': '16.0.0.0.0',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    'description': 'Crea en empledos en la pestaña información privada tres campos para colocar los nombres. apellidos.',
    'depends': ['hr'],
    'data': [
                "data/data_relative_relation.xml",
                "security/ir.model.access.csv",
                "views/hr_employee.xml",
                "views/hr_employee_relative.xml",
    ],
    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'currency': 'USD',
    'price': 0.0
}
