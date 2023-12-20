from odoo import api, fields, models


class HrWorkEntryRegenerationWizard(models.TransientModel):
    _inherit = 'hr.work.entry.regeneration.wizard'

    is_all_employees = fields.Boolean(string='Todos los empleados')

    @api.depends('date_from', 'date_to', 'employee_ids', 'is_all_employees')
    def _compute_search_criteria_completed(self):
        # OVERWRIDE
        for wizard in self:
            wizard.search_criteria_completed = (
                wizard.date_from
                and wizard.date_to
                and (wizard.employee_ids or wizard.is_all_employees)
                and wizard.earliest_available_date
                and wizard.latest_available_date
            )

    @api.onchange('is_all_employees')
    def _onchange_is_all_employees(self):
        self.employee_ids = self.env['hr.employee'].search([]).ids if self.is_all_employees else False
