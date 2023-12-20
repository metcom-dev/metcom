from odoo import models, fields, api


class EpsCredit(models.Model):
    _name = "eps.credit"
    _description = "EPS credit"

    since = fields.Date(string='Desde', required='Tuue')
    until = fields.Date(string='Hasta', required='Tuue')
    affiliated_workers = fields.Integer(string='NÚMERO DE TRABAJADORES AFILIADOS A LA EPS', readonly='False')
    computable_remuneration_health_input = fields.Float(string='REMUNERACIÓN COMPUTABLE APORTE ESSALUD (TODOS AFILIADOS EPS')
    eps_credit = fields.Integer(string='CRÉDITO EPS', readonly='False')
    eps_service_cost = fields.Float(string='COSTO DEL SERVICIO EPS DE LOS TRABAJADORES AFILAIDOS (INCLUYE IGV)')
    uit = fields.Float(string='UIT', readonly='False')
    uit_limit_affiliated_workers = fields.Float(string='LÍMITE DE 10% UIT X NÚMERO DE TRABAJADORES AFILIADOS EPS', readonly='False')
    adjustment = fields.Float(string='AJUSTE')
    final_eps_credit = fields.Float(string='CREDITO EPS FINAL', readonly='False')

    def compute_fields(self):
        affiliated_workers = self.env['hr.employee'].search([('contract_id.state', 'ilike', 'open')])
        workers = []
        for worker in affiliated_workers:
            if worker.health_regime_id.code == '01':
                workers.append(worker)
        self.affiliated_workers = len(workers)

        amount = 0
        for worker in workers:
            for slip in worker.slip_ids:
                if self.since <= slip.date_start_dt <= self.until and slip.state == 'done':
                    for line in slip.line_ids:
                        if line.code == 'ESA_100':
                            amount += line.amount
        self.computable_remuneration_health_input = amount

        self.eps_credit = round(self.computable_remuneration_health_input * 0.09 * 0.25)

        for rec in self.env['various.data.uit'].search([('is_active', '=', 'True')]):
            self.uit = rec.uit_amount

        self.uit_limit_affiliated_workers = self.uit * 0.1 * self.affiliated_workers

        final_eps_credit = min(self.eps_credit, self.eps_service_cost, self.uit_limit_affiliated_workers) if self.eps_service_cost != 0.0 else min(
            self.eps_credit, self.uit_limit_affiliated_workers)
        self.final_eps_credit = self.adjustment if self.adjustment != 0.0 else final_eps_credit
