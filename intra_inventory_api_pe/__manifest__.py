{
    'name': 'Integrates the inventory application of La Tinka (Intralot)',
    'version': '16.0.0.0.0',
    'author': 'Ganemo, Tiam-V',
    'website': 'https://www.ganemo.co',
    'summary': "Integrate Odoo ERP with La Tinka's inventory management api",
    'description': """
     It allows Odoo to be integrated with the La Tinka (Intralot) inventory management system, which is used by the company that provides maintenance to its 
     computer equipment nationwide
    """,
    'category': 'Warehouse',
    'depends': [
        'stock',
        'location_restriction_by_user',
        'warehouse_series_status',
    ],
    'data': [
        'views/stock_picking.xml',
        'views/stock_config_setting.xml',
        'views/stock_quant.xml',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'currency': 'USD',
    'price': 500.00,
}
