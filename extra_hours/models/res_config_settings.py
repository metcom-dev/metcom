from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    min_minutes_extra_hours = fields.Float(
        string='Horas extras',
        config_parameter='extra_hours.min_minutes_extra_hours',
        default=0.0
    )
    diff_extra_part_min = fields.Float(
        string='En minutos',
        config_parameter='extra_hours.diff_extra_part_min',
        default=0.0
    )
