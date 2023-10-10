from odoo import fields
from odoo.tests import common, tagged
from odoo.tests.common import Form
from odoo.tests.common import SavepointCase


@tagged('-at_install', 'post_install')
class TestAutocompleteName(SavepointCase):

    @classmethod
    def setUpClass(self):
        super(TestAutocompleteName, self).setUpClass()
        self.hr_employee = self.env['hr.employee']

    def test_01_onchange_complete_full_name(self):
        employee_form = Form(self.env['hr.employee'], view='hr.view_employee_form')
        employee_form.firstname = u'Jefferson Agustín'
        employee_form.lastname = u'Farfán'
        employee_form.secondname = 'Guadalupe'
        fullname = '{} {} {}'.format(employee_form.firstname, employee_form.lastname, employee_form.secondname)
        self.assertEqual(employee_form.name, fullname)
        print('------------TEST 1 OK - ONCHANGE COMPLETE FULLNAME------------')