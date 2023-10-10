from odoo import api, fields, models

ple_asset_book = [
    ('assets_book_acquisition_asset', '7.1 Registro de Activos Fijos - Adquisiciones - Activo'),
    ('assets_book_acquisition_amortization', '7.1 Registro de Activos Fijos - Adquisiciones - Amortización'),
    ('assets_book_improvements_asset', '7.1 Registro de Activos Fijos - Mejoras - Activo'),
    ('assets_book_other_asset', '7.1 Registro de Activos Fijos - Otros Ajustes - Activo'),
    ('assets_book_other_amortization', '7.1 Registro de Activos Fijos - Otros Ajustes - Amortización'),
    ('assets_book_voluntary_revaluation_asset', '7.1 Registro de Activos Fijos - Reval. Voluntaria - Activo'),
    ('assets_book_voluntary_revaluation_amortization', '7.1 Registro de Activos Fijos - Reval. Voluntaria - Amortización'),
    ('assets_book_revaluation_reorganization_asset', '7.1 Registro de Activos Fijos - Reval. Reorg. - Activo'),
    ('assets_book_revaluation_reorganization_amortization', '7.1 Registro de Activos Fijos - Reval. Reorg. - Amortzación'),
    ('assets_book_revaluation_other_asset', '7.1 Registro de Activos Fijos - Reval. Otras - Activo'),
    ('assets_book_revaluation_other_amortization', '7.1 Registro de Activos Fijos - Reval. Otras - Amortización'),
    ('assets_book_inflation_asset', '7.1 Registro de Activos Fijos - Inflación - Activo'),
    ('assets_book_inflation_amortization', '7.1 Registro de Activos Fijos - Inflación - Amortización')
]


class AccountAsset(models.Model):
    _inherit = 'account.asset'

    asset_catalog_code = fields.Selection(
        selection=[
            ('1', "[1] Naciones Unidas"),
            ('3', "[3] GS1 (EAN-UCC)"),
            ('9', "[9] Otros")],
        string="Catálogo de existencias",
        default='9'
    )
    asset_code = fields.Char(
        string="Código de existencias"
    )
    asset_cubso_osce = fields.Char(
        string="Código CUBSO u OSCE"
    )
    fixed_asset_type = fields.Selection(
        selection=[
            ('1', "[1] Sin efecto tributario"),
            ('2', "[2] Revaluado con Efecto Tributario")],
        string="Tipo de Activo Fijo",
        default='1'
    )
    fixed_asset_state = fields.Selection(
        selection=[
            ('1', "[1] Activos en Desuso"),
            ('2', "[2] Activos Obsoletos"),
            ('9', "[9] Resto de Activos")],
        string="Estado del Activo Fijo",
        default='1'
    )
    depreciation_method = fields.Selection(
        selection=[
            ('1', "[1] Línea Recta"),
            ('2', "[2] Unidades producidas"),
            ('9', "[9] Otros")],
        string="Método de depreciación",
        default='1'
    )
    authorization_number_method_change = fields.Char(string="N° Autorización cambio de método", )
    asset_rate = fields.Float(
        string='Tasa',
        digits=(16, 2)
    )

    first_depreciation_date_import = fields.Date(help="In case of an import from another software, provide the first depreciation date in it.")


class AccountAccount(models.Model):
    _inherit = 'account.account'

    ple_selection = fields.Selection(selection_add=ple_asset_book)

class AccountMove(models.Model):
    _inherit = 'account.move'

    asset_remaining_value = fields.Monetary(string='Depreciable Value', compute='_compute_depreciation_cumulative_value', store=True)
