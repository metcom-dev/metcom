from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    def action_get_additional_certificate(self):
        ids = self.mapped('id')
        if not ids:
            raise ValidationError(u'No hay registros seleccionados.')
        records = self.filtered(lambda x: x.struct_id.additional_certificate)
        additional_certificate = records.mapped('struct_id.additional_certificate')
        if len(additional_certificate) == 1:
            report_name = "setting_voucher.report_additional_report_hr_payslip"
            return self.env.ref(report_name).report_action(records)
        else:
            raise ValidationError(u'No hay reportes adicionales o hay más de uno seleccionado.')


class HrPayrollStructure(models.Model):
    _inherit = 'hr.payroll.structure'

    def get_additional_certificate_name(self):
        certificate_list = self._get_additional_certificate()
        data = list(filter(lambda x: x[0] == self[0].additional_certificate, certificate_list))
        if data:
            return data[0][1]
        else:
            return u'Reporte Adicional'

    @api.model
    def _get_additional_certificate(self):
        selection = []
        return selection

    additional_certificate = fields.Selection(
        selection=lambda x: x.env['hr.payroll.structure']._get_additional_certificate(),
        string=u'Certificado adicional'
    )
