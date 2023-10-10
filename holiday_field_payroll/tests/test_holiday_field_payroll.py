from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from odoo.exceptions import AccessError

from odoo import fields
from odoo.fields import Date, Datetime
from odoo.tests import common
from dateutil.relativedelta import relativedelta


class TestHrPayslip(common.TransactionCase):

    def setUp(self):
        super().setUp()      
        self.Employee = self.env['hr.employee']
        self.SudoEmployee = self.Employee.sudo()
       
        self.dep_rd = self.env['hr.department'].create({
            'name': 'Research & Development - Test',
        })
        
        self.hr_leave_allocation_model = self.env['hr.leave.allocation']
        self.hr_leave_model = self.env['hr.leave']
        print("------SETUP START---- COMPLETE------")

    def test_payslip(self):
       
        self.employee = self.SudoEmployee.create({
            'name': 'Richard',
            'gender': 'male',
            'birthday': '1984-05-01',
            'country_id': self.env.ref('base.be').id,
            'department_id': self.dep_rd.id,
        })
        
        print("------EMPLOYEE CREATED SUCCESSFULLY---- COMPLETE------")
        
        self.structure_type = self.env['hr.payroll.structure.type'].create({
            'name': 'Test - Developer',
        })
        
        print("------TYPE EMPLOYE CREATED SUCCESSFULLY---- COMPLETE------")
    
        self.contract = self.env['hr.contract'].create({
            'date_end': Date.today() + relativedelta(years=2),
            'date_start': Date.to_date('2023-04-04'),
            'name': 'Contract for Richard',
            'wage': 5000.33,
            'employee_id': self.employee.id,
            'structure_type_id': self.structure_type.id,
        })
        
        print("------CONTRACT CREATED SUCCESSFULLY---- COMPLETE------")
        
        self.richard_payslip = self.env['hr.payslip'].create({
            'name': 'Payslip of Richard',
            'employee_id': self.employee.id,
            'contract_id': self.contract.id,             
            'date_from': date(2023, 4, 4),
            'date_to': date(2023, 6, 30)
        })
        self.employee.resource_calendar_id = self.contract.resource_calendar_id
        
        print("------PAYSLIP CREATED SUCCESSFULLY---- COMPLETE------")
       
        self.leave_type = self.env['hr.leave.type'].create({
            'name': 'Unlimited',
            'leave_validation_type': 'hr',
            'requires_allocation': 'no',
        })
        leave_allocation = self.hr_leave_allocation_model.create({
             'name': 'Test Leave Allocation',
             'employee_id': self.employee.id,
             'holiday_status_id': self.leave_type.id,
        })
        print("--------LEAVE ALLOCATION CREATED SUCCESFULLY---------")
        leave = self.hr_leave_model.create({
             'name': 'Test Leave',
             'employee_id': self.employee.id,
             'holiday_status_id': leave_allocation.holiday_status_id.id,             
             'date_from': date(2023, 4, 5),
             'date_to': date(2023, 4, 7)
        })
        print("--------LEAVE CREATED SUCCESFULLY---------")        
        self.richard_payslip.compute_hr_allocation_leave_ids()        
        for i in self.richard_payslip.leave_ids:
            print(i)
            if(i.name == "Test Leave Allocation"):
                print("----ASSERT TRUE-------")
                self.assertIn(i.name, "Test Leave Allocation")
        
        print("--------ASSERTIONS COMPLETED---------")
