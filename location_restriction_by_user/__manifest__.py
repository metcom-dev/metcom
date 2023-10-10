{
    'name': 'Restrict your user\'s access to certain warehouses and locations',
    'version': '16.0.0.0.0',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    'summary': 'In warehouses and locations, you can choose which users will have access to those locations',
    'description': """
    That your inventory users only see those types of operations and locations to which they
    have access. In each warehouse and location you can assign those users who can manage said
    warehouse
    """,
    'category': 'Accounting',
    'depends': ['stock'],
    'data': ['views/views.xml'],
    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'currency': 'USD',
    'price': 125.00,
    'uninstall_hook': '_uninstall_module_complete',
}
