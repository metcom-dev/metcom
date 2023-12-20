from lxml import etree
from odoo import models, fields, api


def get_months_to_update(values):
    data = []
    if 'january_amount' in values:
        data.append('01')
    elif 'february_amount' in values:
        data.append('02')
    elif 'march_amount' in values:
        data.append('03')
    elif 'april_amount' in values:
        data.append('04')
    elif 'may_amount' in values:
        data.append('05')
    elif 'june_amount' in values:
        data.append('06')
    elif 'july_amount' in values:
        data.append('07')
    elif 'august_amount' in values:
        data.append('08')
    elif 'september_amount' in values:
        data.append('09')
    elif 'october_amount' in values:
        data.append('10')
    elif 'november_amount' in values:
        data.append('11')
    elif 'december_amount' in values:
        data.append('12')
    return data


class PayrollProjection(models.Model):
    _name = 'payroll.projection'
    _description = 'Renta de 5ta'

    def _get_line_ids(self):
        return [
            (0, 0, {
                'name': self.env.ref('rent_5ta.payroll_projection_exception_type').name,
                'sequence': 0,
                'exception_id': self.env.ref('rent_5ta.payroll_projection_exception_type').id,
            }),
            (0, 0, {
                'name': self.env.ref('rent_5ta.payroll_projection_exception_01').name,
                'sequence': 1,
                'exception_id': self.env.ref('rent_5ta.payroll_projection_exception_01').id}),
            (0, 0, {
                'name': self.env.ref('rent_5ta.payroll_projection_exception_02').name,
                'sequence': 2,
                'exception_id': self.env.ref('rent_5ta.payroll_projection_exception_02').id}),
            (0, 0, {
                'name': self.env.ref('rent_5ta.payroll_projection_exception_03').name,
                'sequence': 3,
                'exception_id': self.env.ref('rent_5ta.payroll_projection_exception_03').id}),
            (0, 0, {
                'name': self.env.ref('rent_5ta.payroll_projection_exception_04').name,
                'sequence': 4,
                'exception_id': self.env.ref('rent_5ta.payroll_projection_exception_04').id,
                'january_amount': 12,
                'february_amount': 11,
                'march_amount': 10,
                'april_amount': 9,
                'may_amount': 8,
                'june_amount': 7,
                'july_amount': 6,
                'august_amount': 5,
                'september_amount': 4,
                'october_amount': 3,
                'november_amount': 2,
                'december_amount': 1
            }),
            (0, 0, {
                'name': self.env.ref('rent_5ta.payroll_projection_exception_05').name,
                'sequence': 5,
                'exception_id': self.env.ref('rent_5ta.payroll_projection_exception_05').id,
            }),
            (0, 0, {
                'name': self.env.ref('rent_5ta.payroll_projection_exception_06').name,
                'sequence': 6,
                'exception_id': self.env.ref('rent_5ta.payroll_projection_exception_06').id,
            }),
            (0, 0, {
                'name': self.env.ref('rent_5ta.payroll_projection_exception_07').name,
                'sequence': 7,
                'exception_id': self.env.ref('rent_5ta.payroll_projection_exception_07').id,
            }),
            (0, 0, {
                'name': self.env.ref('rent_5ta.payroll_projection_exception_ajus_grati').name,
                'sequence': 8,
                'exception_id': self.env.ref('rent_5ta.payroll_projection_exception_ajus_grati').id,
            }),
            (0, 0, {
                'name': self.env.ref('rent_5ta.payroll_projection_exception_total_grati').name,
                'sequence': 9,
                'exception_id': self.env.ref('rent_5ta.payroll_projection_exception_total_grati').id,
            }),
            (0, 0, {
                'name': self.env.ref('rent_5ta.payroll_projection_exception_10').name,
                'sequence': 10,
                'exception_id': self.env.ref('rent_5ta.payroll_projection_exception_10').id,
            }),
            (0, 0, {
                'name': self.env.ref('rent_5ta.payroll_projection_exception_10_meses_ant').name,
                'sequence': 11,
                'exception_id': self.env.ref('rent_5ta.payroll_projection_exception_10_meses_ant').id,
            }),
            (0, 0, {
                'name': self.env.ref('rent_5ta.payroll_projection_exception_11').name,
                'sequence': 12,
                'exception_id': self.env.ref('rent_5ta.payroll_projection_exception_11').id,
            }),
            (0, 0, {
                'name': self.env.ref('rent_5ta.payroll_projection_exception_year').name,
                'sequence': 13,
                'exception_id': self.env.ref('rent_5ta.payroll_projection_exception_year').id,
            }),
            (0, 0, {
                'name': self.env.ref('rent_5ta.payroll_projection_exception_ajuste_total_ing_anual_proy').name,
                'sequence': 14,
                'exception_id': self.env.ref('rent_5ta.payroll_projection_exception_ajuste_total_ing_anual_proy').id,
            }),
            (0, 0, {
                'name': self.env.ref('rent_5ta.payroll_projection_exception_12').name,
                'sequence': 15,
                'exception_id': self.env.ref('rent_5ta.payroll_projection_exception_12').id,
            }),
            (0, 0, {
                'name': self.env.ref('rent_5ta.payroll_projection_exception_13').name,
                'sequence': 16,
                'exception_id': self.env.ref('rent_5ta.payroll_projection_exception_13').id,
            }),
            (0, 0, {
                'name': self.env.ref('rent_5ta.payroll_projection_exception_14').name,
                'sequence': 17,
                'exception_id': self.env.ref('rent_5ta.payroll_projection_exception_14').id,
            }),
            (0, 0, {
                'name': 'Porcentaje renta de 5ta',
                'sequence': 40,
                'display_type': 'line_section'
            }),
            (0, 0, {
                'name': self.env.ref('rent_5ta.payroll_projection_exception_total_1').name,
                'sequence': 61,
                'exception_id': self.env.ref('rent_5ta.payroll_projection_exception_total_1').id,
            }),
            (0, 0, {
                'name': self.env.ref('rent_5ta.payroll_projection_exception_retencion_otras_empresas').name,
                'sequence': 62,
                'exception_id': self.env.ref('rent_5ta.payroll_projection_exception_retencion_otras_empresas').id,
            }),
            (0, 0, {
                'name': self.env.ref('rent_5ta.payroll_projection_exception_total_2').name,
                'sequence': 63,
                'exception_id': self.env.ref('rent_5ta.payroll_projection_exception_total_2').id,
            }),
            (0, 0, {
                'name': self.env.ref('rent_5ta.payroll_projection_exception_total_3').name,
                'sequence': 64,
                'exception_id': self.env.ref('rent_5ta.payroll_projection_exception_total_3').id,
                'january_amount': 12,
                'february_amount': 12,
                'march_amount': 12,
                'april_amount': 9,
                'may_amount': 8,
                'june_amount': 8,
                'july_amount': 8,
                'august_amount': 5,
                'september_amount': 4,
                'october_amount': 4,
                'november_amount': 4,
                'december_amount': 0
            }),
            (0, 0, {
                'name': self.env.ref('rent_5ta.payroll_projection_exception_total_4').name,
                'sequence': 65,
                'exception_id': self.env.ref('rent_5ta.payroll_projection_exception_total_4').id,
            }),
            (0, 0, {
                'name': 'Retención por participación de utilidades y bonificaciones extraordinarias R2',
                'sequence': 100,
                'display_type': 'line_section'
            }),
            (0, 0, {
                'name': self.env.ref('rent_5ta.payroll_projection_exception_r2_1').name,
                'sequence': 101,
                'exception_id': self.env.ref('rent_5ta.payroll_projection_exception_r2_1').id,
            }),
            (0, 0, {
                'name': self.env.ref('rent_5ta.payroll_projection_exception_09').name,
                'sequence': 102,
                'exception_id': self.env.ref('rent_5ta.payroll_projection_exception_09').id,
            }),
            (0, 0, {
                'name': self.env.ref('rent_5ta.payroll_projection_exception_08').name,
                'sequence': 103,
                'exception_id': self.env.ref('rent_5ta.payroll_projection_exception_08').id,
            }),
            (0, 0, {
                'name': self.env.ref('rent_5ta.payroll_projection_exception_r2_2').name,
                'sequence': 104,
                'exception_id': self.env.ref('rent_5ta.payroll_projection_exception_r2_2').id,
            }),
            (0, 0, {
                'name': 'Porcentaje renta de 5ta',
                'sequence': 150,
                'display_type': 'line_section'
            }),
            (0, 0, {
                'name': self.env.ref('rent_5ta.payroll_projection_exception_total_r2_1').name,
                'sequence': 200,
                'exception_id': self.env.ref('rent_5ta.payroll_projection_exception_total_r2_1').id,
            }),
            (0, 0, {
                'name': self.env.ref('rent_5ta.payroll_projection_exception_total_r2_2').name,
                'sequence': 201,
                'exception_id': self.env.ref('rent_5ta.payroll_projection_exception_total_r2_2').id,
            }),
            (0, 0, {
                'name': self.env.ref('rent_5ta.payroll_projection_exception_total_r2_3').name,
                'sequence': 202,
                'exception_id': self.env.ref('rent_5ta.payroll_projection_exception_total_r2_3').id,
            }),
            (0, 0, {
                'name': self.env.ref('rent_5ta.payroll_projection_exception_total_ajuste_dev_imp_exceso').name,
                'sequence': 203,
                'exception_id': self.env.ref('rent_5ta.payroll_projection_exception_total_ajuste_dev_imp_exceso').id,
            }),
            (0, 0, {
                'name': self.env.ref('rent_5ta.payroll_projection_exception_total_5').name,
                'sequence': 250,
                'exception_id': self.env.ref('rent_5ta.payroll_projection_exception_total_5').id,
            })

        ]

    state = fields.Selection(
        selection=[
            ("open", "Abierto"),
            ("closed", "Cerrado")
        ],
        default="open",
        string='Estado'
    )
    line_ids = fields.One2many(
        comodel_name='payroll.projection.line',
        inverse_name='projection_id',
        string="Conceptos",
        default=_get_line_ids
    )
    employee_id = fields.Many2one(
        comodel_name='hr.employee',
        string="Trabajador",
        readonly=True
    )
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Compañía',
        related='employee_id.company_id'
    )
    date_from = fields.Date(
        string='Desde',
        readonly=True
    )
    date_to = fields.Date(
        string='Hasta',
        readonly=True
    )
    projection_type = fields.Selection(
        selection=[
            ("last_month", "Mes anterior"),
            ("contract", "Contrato")
        ],
        string=u"Tipo de proyección",
    )

    def close_rent_5ta(self):
        self.state = 'closed'

    def open_rent_5ta(self):
        self.state = 'open'

    def name_get(self):
        result = []
        for rec in self:
            result.append((rec.id, "{} [{} | {}]".format(rec.employee_id.name, rec.date_from.strftime('%d-%m-%Y'), rec.date_to.strftime('%d-%m-%Y'))))
        return result

    def recalculate_wizard(self):
        context = self._context
        is_wizard_button_visible = context.get("wizard_button_visible", False)

        return {
            'name': 'Recalcular',
            'view_mode': 'form',
            'view_id': self.env.ref('rent_5ta.recalc_rent_5ta_wizard').id,
            'res_model': 'payroll.projection.wizard.recalc',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'default_wizard_button_visible': is_wizard_button_visible,
                'default_employee_id': [(6, 0, [self.employee_id.id])],
            },
        }

class PayrollProjectionLine(models.Model):
    _name = 'payroll.projection.line'
    _description = 'Renta de 5ta - Línea'
    _order = 'sequence asc'

    state = fields.Selection(
        string='Estado',
        related='projection_id.state',
        store=True
    )
    sequence = fields.Integer(
        string='Secuencia'
    )
    rate_line_id = fields.Many2one(
        comodel_name='rates.fifth_rent.line',
        string="Linea tasa de renta 5ta"
    )
    projection_id = fields.Many2one(
        comodel_name='payroll.projection',
        ondelete='cascade',
        string="Renta 5ta"
    )
    exception_id = fields.Many2one(
        comodel_name='payroll.projection.exception',
        string="Excepccion",
        readonly=True
    )
    name = fields.Text(
        string='Concepto',
        readonly=True
    )
    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False, help="Technical field for UX purpose.")
    type_rate_rent = fields.Selection([
        ('r1', "R1"),
        ('r2', "R2")],
        default=False,
        string="Tipo de renta - tasas"
    )
    january_amount = fields.Char(
        string='Enero',
        readonly=True
    )
    february_amount = fields.Char(
        string='Febrero',
        readonly=True
    )
    march_amount = fields.Char(
        string='Marzo',
        readonly=True
    )
    april_amount = fields.Char(
        string='Abril',
        readonly=True
    )
    may_amount = fields.Char(
        string='Mayo',
        readonly=True
    )
    june_amount = fields.Char(
        string='Junio',
        readonly=True
    )
    july_amount = fields.Char(
        string='Julio',
        readonly=True
    )
    august_amount = fields.Char(
        string='Agosto',
        readonly=True
    )
    september_amount = fields.Char(
        string='Setiembre',
        readonly=True
    )
    october_amount = fields.Char(
        string='Octubre',
        readonly=True
    )
    november_amount = fields.Char(
        string='Noviembre',
        readonly=True
    )
    december_amount = fields.Char(
        string='Diciembre',
        readonly=True
    )

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(PayrollProjectionLine, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        if view_type == 'tree':
            doc = etree.XML(res['arch'])
            fields = [
                'january_amount',
                'february_amount',
                'march_amount',
                'april_amount',
                'may_amount',
                'june_amount',
                'july_amount',
                'august_amount',
                'september_amount',
                'october_amount',
                'november_amount',
                'december_amount',
            ]
            rem_id = self.env.ref('rent_5ta.payroll_projection_exception_10', False)
            ajustes_grati = self.env.ref('rent_5ta.payroll_projection_exception_ajus_grati', False)
            ajustes_id = self.env.ref('rent_5ta.payroll_projection_exception_11', False)
            ajust_year_id = self.env.ref('rent_5ta.payroll_projection_exception_year', False)
            a_tot_pry_id = self.env.ref('rent_5ta.payroll_projection_exception_ajuste_total_ing_anual_proy', False)
            a_dev_imp_id = self.env.ref('rent_5ta.payroll_projection_exception_total_ajuste_dev_imp_exceso', False)
            ret_otra_emp_id = self.env.ref('rent_5ta.payroll_projection_exception_retencion_otras_empresas', False)
            for field in fields:
                value = "//field[@name='%s']" % field
                for node in doc.xpath(value):
                    mod = '{"readonly": ["|",["exception_id","not in",[%d,%d,%d,%d,%d,%d,%d]],["state","=","closed"]]}'
                    mod = mod % (ajustes_id.id, ajustes_grati.id, ajust_year_id.id, rem_id.id, a_tot_pry_id.id, a_dev_imp_id.id, ret_otra_emp_id.id)
                    node.set("modifiers", mod)

            for node in doc.xpath('/tree'):
                uits_id = self.env.ref('rent_5ta.payroll_projection_exception_13', False)
                ret_meses_ant_id = self.env.ref('rent_5ta.payroll_projection_exception_total_1', False)
                anual_rem_ord_id = self.env.ref('rent_5ta.payroll_projection_exception_total_r2_1', False)
                d_danger = 'exception_id in [{}, {}, {}]'.format(uits_id.id, ret_meses_ant_id.id, anual_rem_ord_id.id)
                node.set("decoration-danger", d_danger)

                tot_ing_anual_proy_id = self.env.ref('rent_5ta.payroll_projection_exception_12', False)
                renta_neta_anual_proy_id = self.env.ref('rent_5ta.payroll_projection_exception_14', False)
                rem_comp_mensual_id = self.env.ref('rent_5ta.payroll_projection_exception_03', False)
                tot_rem_proy_per_id = self.env.ref('rent_5ta.payroll_projection_exception_05', False)
                tot_renta_anual_proy_id = self.env.ref('rent_5ta.payroll_projection_exception_total_2', False)
                factor_id = self.env.ref('rent_5ta.payroll_projection_exception_total_3', False)
                rent_mensual_r1_id = self.env.ref('rent_5ta.payroll_projection_exception_total_4', False)
                renta_neta_id = self.env.ref('rent_5ta.payroll_projection_exception_r2_1', False)
                total_renta_neta_id = self.env.ref('rent_5ta.payroll_projection_exception_r2_2', False)
                ret_afect_concept_extra_id = self.env.ref('rent_5ta.payroll_projection_exception_total_r2_2', False)
                ret_total_id = self.env.ref('rent_5ta.payroll_projection_exception_total_r2_3', False)
                dev_imp_id = self.env.ref('rent_5ta.payroll_projection_exception_total_5', False)
                a_dev_imp_id = self.env.ref('rent_5ta.payroll_projection_exception_total_ajuste_dev_imp_exceso', False)
                a_tot_pry_id = self.env.ref('rent_5ta.payroll_projection_exception_ajuste_total_ing_anual_proy', False)
                d_bf = 'exception_id in [{},{},{},{},{},{},{},{},{},{},{},{}, {}]'.format(tot_ing_anual_proy_id.id,
                                                                                          renta_neta_anual_proy_id.id,
                                                                                          rem_comp_mensual_id.id,
                                                                                          tot_rem_proy_per_id.id,
                                                                                          tot_renta_anual_proy_id.id,
                                                                                          factor_id.id,
                                                                                          rent_mensual_r1_id.id,
                                                                                          renta_neta_id.id,
                                                                                          total_renta_neta_id.id,
                                                                                          a_tot_pry_id.id,
                                                                                          ret_afect_concept_extra_id.id,
                                                                                          ret_total_id.id,
                                                                                          a_dev_imp_id.id,
                                                                                          dev_imp_id.id)
                node.set("decoration-bf", d_bf)

            res['arch'] = etree.tostring(doc, encoding='unicode')
        return res

    @api.onchange('january_amount')
    def calc_per_year_total_january(self):
        if self.exception_id.name == 'Ajuste en Años' or self.exception_id.name == 'Ajuste de Gratificación' and self.january_amount:
            self.february_amount = self.january_amount
            self.march_amount = self.february_amount
            self.april_amount = self.march_amount
            self.may_amount = self.april_amount
            self.june_amount = self.may_amount
            self.july_amount = self.june_amount
            self.august_amount = self.july_amount
            self.september_amount = self.august_amount
            self.october_amount = self.september_amount
            self.november_amount = self.october_amount
            self.december_amount = self.november_amount

    @api.onchange('february_amount')
    def calc_per_year_total_february(self):
        if self.exception_id.name == 'Ajuste en Años' or self.exception_id.name == 'Ajuste de Gratificación' and self.february_amount:
            self.march_amount = self.february_amount
            self.april_amount = self.march_amount
            self.may_amount = self.april_amount
            self.june_amount = self.may_amount
            self.july_amount = self.june_amount
            self.august_amount = self.july_amount
            self.september_amount = self.august_amount
            self.october_amount = self.september_amount
            self.november_amount = self.october_amount
            self.december_amount = self.november_amount

    @api.onchange('march_amount')
    def calc_per_year_total_march(self):
        if self.exception_id.name == 'Ajuste en Años' or self.exception_id.name == 'Ajuste de Gratificación' and self.march_amount:
            self.april_amount = self.march_amount
            self.may_amount = self.april_amount
            self.june_amount = self.may_amount
            self.july_amount = self.june_amount
            self.august_amount = self.july_amount
            self.september_amount = self.august_amount
            self.october_amount = self.september_amount
            self.november_amount = self.october_amount
            self.december_amount = self.november_amount

    @api.onchange('april_amount')
    def calc_per_year_total_april(self):
        if self.exception_id.name == 'Ajuste en Años' or self.exception_id.name == 'Ajuste de Gratificación' and self.april_amount:
            self.may_amount = self.april_amount
            self.june_amount = self.may_amount
            self.july_amount = self.june_amount
            self.august_amount = self.july_amount
            self.september_amount = self.august_amount
            self.october_amount = self.september_amount
            self.november_amount = self.october_amount
            self.december_amount = self.november_amount

    @api.onchange('may_amount')
    def calc_per_year_total_may(self):
        if self.exception_id.name == 'Ajuste en Años' or self.exception_id.name == 'Ajuste de Gratificación' and self.may_amount:
            self.june_amount = self.may_amount
            self.july_amount = self.june_amount
            self.august_amount = self.july_amount
            self.september_amount = self.august_amount
            self.october_amount = self.september_amount
            self.november_amount = self.october_amount
            self.december_amount = self.november_amount

    @api.onchange('june_amount')
    def calc_per_year_total_june(self):
        if self.exception_id.name == 'Ajuste en Años' or self.exception_id.name == 'Ajuste de Gratificación' and self.june_amount:
            self.july_amount = self.june_amount
            self.august_amount = self.july_amount
            self.september_amount = self.august_amount
            self.october_amount = self.september_amount
            self.november_amount = self.october_amount
            self.december_amount = self.november_amount

    @api.onchange('july_amount')
    def calc_per_year_total_july(self):
        if self.exception_id.name == 'Ajuste en Años' or self.exception_id.name == 'Ajuste de Gratificación' and self.july_amount:
            self.august_amount = self.july_amount
            self.september_amount = self.august_amount
            self.october_amount = self.september_amount
            self.november_amount = self.october_amount
            self.december_amount = self.november_amount

    @api.onchange('august_amount')
    def calc_per_year_total_august(self):
        if self.exception_id.name == 'Ajuste en Años' or self.exception_id.name == 'Ajuste de Gratificación' and self.august_amount:
            self.september_amount = self.august_amount
            self.october_amount = self.september_amount
            self.november_amount = self.october_amount
            self.december_amount = self.november_amount

    @api.onchange('september_amount')
    def calc_per_year_total_september(self):
        if self.exception_id.name == 'Ajuste en Años' or self.exception_id.name == 'Ajuste de Gratificación' and self.september_amount:
            self.october_amount = self.september_amount
            self.november_amount = self.october_amount
            self.december_amount = self.november_amount

    @api.onchange('october_amount')
    def calc_per_year_total_october(self):
        if self.exception_id.name == 'Ajuste en Años' or self.exception_id.name == 'Ajuste de Gratificación' and self.october_amount:
            self.november_amount = self.october_amount
            self.december_amount = self.november_amount

    @api.onchange('november_amount')
    def calc_per_year_total_november(self):
        if self.exception_id.name == 'Ajuste en Años' or self.exception_id.name == 'Ajuste de Gratificación' and self.november_amount:
            self.december_amount = self.november_amount

    def write(self, vals):
        res = super(PayrollProjectionLine, self).write(vals)
        rem_id = self.env.ref('rent_5ta.payroll_projection_exception_10', False)
        rem_meses_ant = self.env.ref('rent_5ta.payroll_projection_exception_10_meses_ant', False)
        ajustes_id = self.env.ref('rent_5ta.payroll_projection_exception_11', False)
        a_tot_pry_id = self.env.ref('rent_5ta.payroll_projection_exception_ajuste_total_ing_anual_proy', False)
        a_dev_imp_id = self.env.ref('rent_5ta.payroll_projection_exception_total_ajuste_dev_imp_exceso', False)
        ret_otra_emp_id = self.env.ref('rent_5ta.payroll_projection_exception_retencion_otras_empresas', False)
        ajust_year = self.env.ref('rent_5ta.payroll_projection_exception_year', False)
        ajustes_grati = self.env.ref('rent_5ta.payroll_projection_exception_ajus_grati', False)
        # reuse wizard's functions
        wizard = self.env['payroll.projection.wizard']

        if self.exception_id == ajust_year:
            data = get_months_to_update(vals)
            mounth_data = int(data[0])
            for i in range(mounth_data, 13):
                alpha = str(i)
                if alpha in ['1', '2', '3', '4', '5', '6', '7', '8', '9']:
                    alpha = '0' + alpha
                wizard.get_amount_total_anual_proyectado(self.projection_id, [alpha])
                wizard.get_amount_total_renta_anual_proyectada(self.projection_id, [alpha])

        if self.exception_id == ajustes_grati:
            data = get_months_to_update(vals)
            mounth_data = int(data[0])
            for i in range(mounth_data, 13):
                alpha = str(i)
                if alpha in ['1', '2', '3', '4', '5', '6', '7', '8', '9']:
                    alpha = '0' + alpha
                wizard.get_amount_total_gratificacion(self.projection_id, [alpha])
                wizard.get_amount_total_anual_proyectado(self.projection_id, [alpha])

        if self.exception_id == rem_id:
            data = get_months_to_update(vals)
            mounth_data = int(data[0])
            for i in range(mounth_data, 13):
                alpha = str(i)
                if alpha in ['1', '2', '3', '4', '5', '6', '7', '8', '9']:
                    alpha = '0' + alpha
                wizard.get_amount_rem_percibidas_meses_ant(self.projection_id, [alpha])

        if self.exception_id in [ajustes_id, rem_meses_ant, a_tot_pry_id, a_dev_imp_id, ret_otra_emp_id]:
            data = get_months_to_update(vals)
            for month in data:
                wizard.get_amount_total_anual_proyectado(self.projection_id, [month])
                wizard.get_amount_total_renta_anual_proyectada(self.projection_id, [month])
                wizard.get_calc_lines_rates_r1(self.projection_id, [month])
                wizard.get_amount_renta_neta(self.projection_id, [month])
                wizard.get_amount_total_renta_neta(self.projection_id, [month])
                wizard.get_calc_lines_rates_r2(self.projection_id, [month])
                wizard.get_amount_rem_ordinarias(self.projection_id, [month])
                wizard.get_amount_retenciones_meses_ant(self.projection_id, [
                    '{}/{}'.format(month, self.projection_id.date_from.strftime('%Y'))], self.projection_id.employee_id)
                wizard.get_amount_tot_renta_anual_proyectado(self.projection_id, [month])
                wizard.get_amount_retencion_afectada_extraordinarias(self.projection_id, [month])
                wizard.get_amount_retencion_1(self.projection_id, [month])
                wizard.get_amount_retencion_total(self.projection_id, [month])
                wizard.get_amount_devolucion_impuesto_retenido(self.projection_id, [month])
        return res

    def query_update_line(self, month, total, line_6):
        query = """UPDATE payroll_projection_line SET """ + month + """=%s WHERE id=%s """ % (total, str(line_6.id).replace('NewId_', ''))
        self._cr.execute(query)


class PayrollProjectionException(models.Model):
    _name = 'payroll.projection.exception'
    _description = 'Línea Renta 5ta - Excepción'

    name = fields.Char(string="Concepto", readonly=True)
    is_active = fields.Boolean(string='¿Esta activo?')
