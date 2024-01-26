from odoo import api, fields, models
from odoo.exceptions import ValidationError


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    life_insurance = fields.Boolean(
        string='Seguro de vida?',
        groups="hr.group_hr_user"
    )
    life_insurance_id = fields.Many2one(
        comodel_name='life.insurance',
        string='Póliza seguro de vida',
        store=True,
        groups="hr.group_hr_user"
    )
    button_activate = fields.Boolean(
        string='Guardar empleado en la poliza',
        groups="hr.group_hr_user",
        default=False
    )

    @api.onchange('life_insurance','life_insurance_id.employees_ids')
    def _onchange_life_insurance(self):
        
        for record in self: 
            most_recent_policy = self.env['life.insurance'].search([
                    ('employees_ids', 'in', record._origin.id),
                ], order='end_date desc', limit=1)
            
            if most_recent_policy:
                record.life_insurance_id = most_recent_policy
    
    @api.onchange('button_activate')
    def _onchange_button_activate(self):

        for record in self:

            if record.life_insurance and record.button_activate:
                life_insurance_record = record.life_insurance_id
                life_insurance_record.write({
                    'employees_ids': [(4, record._origin.id, False)]
                })

                record.button_activate = False