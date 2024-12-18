# custom_addons/om_hr_payroll/models/employee_tax_report.py

from odoo import models, api
import calendar
from datetime import datetime
class EmployeeBankLetterReport(models.AbstractModel):
    _name = 'report.om_hr_payroll.employee_bank_letter_report'
    _description = 'Employee Bank Letter Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        company = self.env.company
        currency = company.currency_id
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

        single_page_employee = []
        net = 0
        for payslip in payslips:
            for line in payslip.line_ids:
                if (line.code == 'NET'):
                    net += int(line.total)
        if currency:
            net_in_words = currency.amount_to_text(net)
            currency_name = currency.currency_unit_label
            net_in_words = net_in_words.replace(currency_name, '').strip()
        else:
            net_in_words = ''

        return {
            'company': company,
            'net':net,
            'net_in_words':net_in_words,
            'bank_name':data.get('bank_name'),
            'bank_branch':data.get('bank_branch') ,
            'company_bank_account':data.get('company_bank_account') ,
            'company_bank_account_branch':data.get('company_bank_account_branch'),
            'company_branch':data.get('company_branch'),
            'month':datetime.strptime(data.get('month'), "%m").strftime("%B")
        }
