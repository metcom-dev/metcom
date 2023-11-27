{
    'name': 'Work Entry Modified',
    'version': '16.0.0.0.1',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    'category': 'Payroll',
    'summary': " Configure the types of work tickets, indicating position on the ticket, if it is not paid, rounding, etc.",
    'description': """
     Configure the types of work tickets, indicating position on the ticket, if it is not paid, rounding, etc.
    """,
    'depends': ['hr_payroll', 'voucher_lbs', 'payroll_utilities', 'voucher_payroll', 'basic_rule', 'holiday_rule',
                'legal_benefits_rule', 'rules_utilities'],
    'data': [
        'data/hr_work_entry_type_data.xml',
        'data/hr_salary_rule_category_data.xml'
    ],
    'post_init_hook': '_entry_change',
    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'currency': 'USD',
    'price': 0.0
}
