from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    risk_activities_sctr = fields.Boolean(
        string='Actividades de riesgo SCTR',
        config_parameter='hr_contract.risk_activities_sctr',
    )


