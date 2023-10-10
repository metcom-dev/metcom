from odoo.tests.common import TransactionCase


class TestHrPayrollStructure(TransactionCase):

    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        user_admin = self.env.ref("base.user_admin")
        self.env = self.env(user=user_admin)
        self.HrPayrollStructure = self.env["hr.payroll.structure"]
        self.HrPayrollStructureType = self.env["hr.payroll.structure.type"]

        self.structure_type = self.HrPayrollStructureType.create({
            "name": "Estructura de Prueba",
        })

        self.structure = self.HrPayrollStructure.create({
            "name": "Structure 1",
            "type_id": self.structure_type.id,
        })
        print("SetUp HR OK ...... !!!!")

    def test_get_additional_certificate(self):
        "Check additional certificate selection"
        additional_certificate = self.structure._get_additional_certificate()
        self.assertIn(('cts', 'CTS Liquidación'), additional_certificate)
        print("Test get_additional_certificate HR OK ...... !!!!")
        print("=============================================")
        print("=============================================")
