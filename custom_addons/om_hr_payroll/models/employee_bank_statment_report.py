# custom_addons/om_hr_payroll/models/employee_tax_report.py

from odoo import models, api
from datetime import datetime
import calendar
class EmployeeBankStatementReport(models.AbstractModel):
    _name = 'report.om_hr_payroll.report_employee_bank_statement_report'
    _description = ''

    @api.model
    def _get_report_values(self, docids, data=None):
        company = self.env.company
        username = self.env.user.name
        payslips = self.env['hr.payslip'].search([('state','=','done')])
        selected_month = data.get('month')
        selected_year = data.get('year')
        start_date = f"{selected_year}-{selected_month}-01"
        last_day = calendar.monthrange(int(selected_year), int(selected_month))[1]

        end_date = f"{selected_year}-{selected_month}-{last_day}"  # Covers all possible dates in the month
        branch_id = data.get('branch_id')
        domain = [('state', '=', 'done'),
                  ('date_from', '>=', start_date),
                  ('date_to', '<=', end_date), ]
        if branch_id:
            domain.append(('employee_id.employee_branch', '=', int(branch_id)))
        payslips = self.env['hr.payslip'].search(domain)


        employee_bank_statement = []
        payslip_period = '' f"{selected_month}.{selected_year}"
        current_date = datetime.now().strftime('%d.%m.%y')
        single_page_employee = []
        count = 1
        total = 0
        for payslip in payslips:
            employee = payslip.employee_id
            bank_account_number = ""
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
            total += net
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
            'current_date':current_date,
            'total':total,
            'username':username
        }
