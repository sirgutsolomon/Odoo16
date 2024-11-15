# custom_addons/om_hr_payroll/models/employee_tax_report.py

from odoo import models, api
from datetime import datetime
class EmployeeTaxReport(models.AbstractModel):
    _name = 'report.om_hr_payroll.report_employee_payroll_summary'
    _description = 'Employee Payroll Summary'

    @api.model
    def _get_report_values(self, docids, data=None):
        # Retrieve data passed from wizard
        headoffice = data.get('headoffice')

        # Fetch company and employee details, process as needed
        company = self.env.company
        payslips = self.env['hr.payslip'].search([('state','=','done')])  # Get all employees or apply any filters as needed

        employee_tax_data = []
        payslip_period = ''
        current_date = datetime.now().strftime('%d-%m-%y')
        single_page_employee = []
        for payslip in payslips:
            if(payslip.date_from):
                payslip_period = payslip.date_from.strftime('%Y-%m')

            employee = payslip.employee_id
            totalAllowance = 0
            basic_salary = 0
            gross_salary = 0
            income_tax = 0
            employee_pension = 0
            total_deduction = 0
            net = 0

            for line in payslip.line_ids:
                if (line.code == 'BASIC'):
                    basic_salary += int(line.total)
                if (line.code == 'INCOMETAX'):
                    income_tax += int(line.total)
                if (line.code == 'PENSION'):
                    employee_pension += int(line.total)
                if (line.code == 'TOTALDEDUCTION'):
                    total_deduction += int(line.total)
                if (line.code == 'NET'):
                    net += int(line.total)
                if (line.category_id.name == "Allowance"):
                    totalAllowance += int(line.total)
                if line.category_id.name == "Gross":
                    gross_salary += int(line.total)
            single_page_employee.append(
                {
                    'id_no': employee.id_no,
                    'name': employee.legal_name,
                    'basic_salary': basic_salary,
                    'over_time': '',
                    'other_addition': '',
                    'total_allowance': totalAllowance,
                    'gross_salary': gross_salary,
                    'income_tax': income_tax,
                    'other_deduction': '',
                    'employee_pension': employee_pension,
                    'total_deduction': total_deduction,
                    'net': net,
                }

            )
            if len(single_page_employee) == 20:
                employee_tax_data.append(single_page_employee)
                single_page_employee = []
        if(single_page_employee):
            employee_tax_data.append(single_page_employee)
        return {
            'company': company,
            'employees': employee_tax_data,
            'headoffice': headoffice,
            'payslip_period':payslip_period,
            'current_date':current_date
        }
