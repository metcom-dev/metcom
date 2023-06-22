from odoo.tests import Form
from odoo.addons.hr.tests.common import TestHrCommon
from datetime import datetime


class TestProcessPlame(TestHrCommon):

    def setUp(self):
        super().setUp()

        self.process_plame = self.env['plame.files'].create({
            'date_from': datetime(2023, 4, 1),
            'date_to': datetime(2023, 6, 30),
            'company_id': '1',
        })

    def test_generate_files_process_plame(self):
        self.process_plame.generate_files()
        print('------TEST PROCESS PLAME OK--------------')