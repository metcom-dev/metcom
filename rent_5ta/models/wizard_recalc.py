from odoo import models, fields

class PayrollProjectionWizardRecalc(models.TransientModel):
    _name = 'payroll.projection.wizard.recalc'
    _description = 'Recalcular Renta de 5ta'

    date_from = fields.Date(
        string='Desde',
        required=True
    )
    date_to = fields.Date(
        string='Hasta',
        required=True
    )

    employee_id = fields.Many2many(
        comodel_name='hr.employee',
        string='Empleados'
    )

    def recalc_rent_5ta(self):
        projection = self.env['payroll.projection.wizard'].search([
            ('date_from', '<=', self.date_from),
            ('date_to', '>=', self.date_to),
        ], order='id desc', limit=1)

        recalc_wizard = self.env['payroll.projection.wizard'].create({
            'date_from': self.date_from,
            'date_to': self.date_to,
            'select_employee': True,
            'employees_ids': self.employee_id.ids,
            'projection_type': projection.projection_type,
        })

        recalc_wizard.calc_rent_5ta()