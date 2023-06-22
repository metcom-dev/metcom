{
    'name': 'Extra hours',
    'version': '16.0.0.0.0',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    'category': 'Payroll',
    'description': """
Este modulo crea un modelo en Partes de Horas donde se registran las horas extras de cada trabajador y se calculan 
automaticas, cuando el representante aprueba estas horas extras migran al modulo de planilla para su respectivo pago.

Tambien crea en asistencia dos columanas una llamada "Horas extras" y otra "Parte de Horas" las cuales pueden 
ayudar a una analisis de planilla, Horas extras le calcula el tiempo adicional que tuvo el trabajador en la empresa 
para que puedan evaluar si son horas afectas o no, y Partes de Horas muestra lo aprobado por cada supervisor, 
asi facilmente pueden ver si existe algun error en el registro de parte de horas.
    """,
    'depends': [
        'automatic_timesheets',
        'hr_attendance'
    ],
    'data': [
        'views/account_analytic_line_views.xml',
        'views/hr_attendance_views.xml',
        'views/project_task_views.xml',
        'views/res_config_settings_views.xml'
    ],
    'assets': {
        'web.assets_backend': [
            'extra_hours/static/src/css/classes.css',
        ],
    },
    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'currency': 'USD',
    'price': 0.00
}
