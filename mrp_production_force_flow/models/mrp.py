from odoo import models


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    def button_mark_done(self):
        self._button_mark_done_sanity_checks()
        for production in self:
            # Valida en la orden de producción si el campo "move_finished_ids" se encuentre lleno, ya que de el se calcula varios campos adicionales
            # Sino no lo estuviera fuerza a volver a calcularce ya que solo se ejecuta al inicio de la orden el metodo _create_update_move_finished
            if not production.move_finished_ids:
                production._create_update_move_finished()
        return super(MrpProduction, self).button_mark_done()

    def action_cancel(self):
        for production in self:
            # Valida en la orden de producción si el campo "move_finished_ids" se encuentre lleno, ya que la condicional valida si esta lleno para
            # mandarlo a cancelado. Sino no lo estuviera fuerza a volver a calcularce ya que solo se ejecuta al inicio de la orden
            # el metodo _create_update_move_finished
            if not production.move_finished_ids:
                production._create_update_move_finished()
        return super(MrpProduction, self).action_cancel()
