from odoo import api, models, fields


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def generate_data_blank_delivery(self):
        
        note = ""
        if self.note:
            note = note + self.note + " "
        if self.l10n_pe_edi_observation:
            note += self.l10n_pe_edi_observation
        
        values = {
            'date_done': self.date_done.strftime('%d/%m/%Y') if self.date_done else "",
            'reference': self.name,
            'transfer_start_date': self.l10n_pe_edi_departure_start_date.strftime('%d/%m/%Y') if self.l10n_pe_edi_departure_start_date else "",
            'contact': self.partner_id.name or "",
            'vat': self.partner_id.vat or "",
            'plate_number': self.l10n_pe_edi_vehicle_id.license_plate if self.l10n_pe_edi_vehicle_id else "",
            'driver_license': self.l10n_pe_edi_vehicle_id.operator_id.l10n_pe_edi_operator_license or "" if self.l10n_pe_edi_transport_type == '02' else "",
            'note': note,
            'carrier_partner_id_name': self.l10n_pe_operator_id.name or "" if self.l10n_pe_edi_transport_type == '01' else "",
            'carrier_partner_id_vat': self.l10n_pe_operator_id.vat or "" if self.l10n_pe_edi_transport_type == '01' else "",
            'picking_number': self.picking_number[4:] if self.picking_number else "",
        }
        return values


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    def _get_aggregated_product_quantities(self, **kwargs):
        """ Returns a dictionary of products add weight (key = id+name+description+uom+weight) and corresponding values of interest."""
        res = super(StockMoveLine, self)._get_aggregated_product_quantities()
        for move_line in res.values():
            move_line["weight"] = move_line["product"].weight
        return res
