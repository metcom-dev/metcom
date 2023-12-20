from odoo.tests.common import TransactionCase
from odoo.exceptions import AccessError


class TestSectionLbs(TransactionCase):

 def setUp(self):
        super(TestSectionLbs, self).setUp()
        self.section_model = self.env['section.lbs']
        print("*"*50)

 def test_name_get(self):
    section = self.section_model.create({'code': '1', 'description': 'Sección 1'})

    name_get_result = section.name_get()

    self.assertEqual(len(name_get_result), 1)

    expected_name = (section.id, '[1] Sección 1')

    self.assertEqual(name_get_result[0], expected_name, "El método name_get no devuelve el nombre esperado")

    empty_result = self.section_model.browse([]).name_get()

    self.assertEqual(empty_result, [], "El método name_get debe devolver una lista vacía para una lista vacía de secciones")
    print("/m"*60)

