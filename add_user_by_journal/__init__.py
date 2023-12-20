from . import models


def _uninstall_module_complete(cr, registry):
    cr.execute("""UPDATE ir_act_window SET domain = '[]' WHERE ir_act_window.name->>'en_US' = 'Accounting Dashboard';""")
    cr.execute("""UPDATE ir_act_window SET domain = '[]' WHERE ir_act_window.name->>'en_US' = 'Journals';""")
