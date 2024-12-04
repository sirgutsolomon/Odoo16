# custom_addons/om_hr_payroll/models/employee_tax_report.py

from odoo import models, api
from datetime import datetime
import calendar
class EmployeeTaxReport(models.AbstractModel):
    _name = 'report.om_hr_payroll.report_employee_payroll_summary'
    _description = 'Employee Payroll Summary'

    @api.model
    def _get_report_values(self, docids, data=None):
        # Retrieve data passed from wizard
        headoffice = data.get('headoffice')
        selected_month = data.get('month')
        selected_year = data.get('year')
        start_date = f"{selected_year}-{selected_month}-01"
        last_day = calendar.monthrange(int(selected_year), int(selected_month))[1]

        end_date = f"{selected_year}-{selected_month}-{last_day}"  # Covers all possible dates in the month

        company = self.env.company
        branch_id = data.get('branch_id')
        domain = [('state','=','done'),
            ('date_from', '>=', start_date),
            ('date_to', '<=', end_date),]
        if branch_id:
            domain.append(('employee_id.employee_branch', '=', int(branch_id)))
        payslips = self.env['hr.payslip'].search(domain)

        employee_tax_data = []
        payslip_period = f"{selected_month}.{selected_year}"
        current_date = datetime.now().strftime('%d.%m.%y')
        single_page_employee = []
        for payslip in payslips:

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
