from odoo import api, fields, models


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    def _get_new_worked_days_lines(self):
        if self.struct_id.use_worked_day_lines:
            # computation of the salary worked days
            struct_days_ids = self.struct_id.struct_days_ids.ids
            worked_days_line_values = list(filter(lambda x: x['work_entry_type_id'] not in struct_days_ids, self._get_worked_day_lines()))
            return [(5, 0, 0)] + [(0, 0, vals) for vals in worked_days_line_values]
        else:
            return [(5, False, False)]

    @staticmethod
    def delete_restricted_days_by_struct(res, struct_id):
        if struct_id and struct_id.struct_days_ids:
            codes = struct_id.struct_days_ids.mapped('code')
            res = list(filter(lambda x: x['code'] not in codes, res))
        return res


class HrPayrollStructure(models.Model):
    _inherit = 'hr.payroll.structure'

    struct_days_ids = fields.Many2many(
        comodel_name='hr.work.entry.type',
        string=u'Reglas Días',
    relation="struct_days_ids_hr_payroll_structure_hr_work_entry_type_rel",
    )
