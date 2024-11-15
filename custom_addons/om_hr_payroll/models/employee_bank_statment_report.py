# custom_addons/om_hr_payroll/models/employee_tax_report.py

from odoo import models, api
from datetime import datetime
class EmployeeBankStatementReport(models.AbstractModel):
    _name = 'report.om_hr_payroll.report_employee_bank_statement_report'
    _description = 'Employee Bank Statement'

    @api.model
    def _get_report_values(self, docids, data=None):

        company = self.env.company
        payslips = self.env['hr.payslip'].search([('state','=','done')])  # Get all employees or apply any filters as needed

        employee_bank_statement = []
        payslip_period = ''
        current_date = datetime.now().strftime('%d-%m-%y')
        single_page_employee = []
        count = 1
        for payslip in payslips:
            if(payslip.date_from):
                payslip_period = payslip.date_from.strftime('%Y-%m')

            employee = payslip.employee_id
            bank_account_number = "No Bank Account"
            if employee.bank_account_id:
                bank_account_number = employee.bank_account_id.acc_number
            net = 0
            for line in payslip.line_ids:
                if (line.code == 'NET'):
                    net += int(line.total)
            single_page_employee.append(
                {
                    's_no': count,
                    'name': employee.legal_name,
                    'bank_account_number':bank_account_number,
                    'net': net,
                }

            )
            count += 1
            if len(single_page_employee) == 20:
                employee_bank_statement.append(single_page_employee)
                single_page_employee = []
        if(single_page_employee):
            employee_bank_statement.append(single_page_employee)
        return {
            'company': company,
            'employees': employee_bank_statement,
            'payslip_period':payslip_period,
            'current_date':current_date
        }
