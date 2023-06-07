from odoo import models, fields, api
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError

import logging
log = logging.getLogger(__name__)

class WizardPreorderProject(models.TransientModel):
    _name = 'wizard.preorder_for_project'
    _description = 'Reporte de pre-ordenes por proyecto'

    project_id = fields.Many2one('project.project', string='Proyecto', required=True)
    
    def generate_report(self):
        log.info('generate_report')
        return {
            'type': 'ir.actions.report',
            'report_name': 'report_preorders_project.report_preorder_project_xlsx',
            'report_type': 'xlsx',
            'lines': self,
            'data': {
                'project_id': self.project_id.id,
            },
        }
