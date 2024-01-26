{
    'name': 'Renta de quinta',
    'summary': 'It is in charge of creating a complete model for the calculation of fifth rent, considering all the parameters established by SUNAT',
    'version': '16.0.0.2.2',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    'description': 'It is in charge of creating a complete model for the calculation of fifth rent, considering all the parameters established by SUNAT',
    'depends': [
        'basic_rule',
        'additional_fields_voucher',
        'employee_service_contract',
        'hr_work_entry_contract_enterprise',
    ],
    'data': [
        'data/hr_data.xml',
        'data/payroll_projection_exception_data.xml',
        'data/payroll_projection_data.xml',
        'security/ir.model.access.csv',
        'views/hr_views.xml',
        'views/payroll_projection_views.xml',
        'views/rate_fifth_rent_views.xml',
        'views/reports.xml',
        'views/wizards.xml',
        'views/wizard_recalc.xml'
    ],
    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'currency': 'USD',
    'price': 0.00
}
