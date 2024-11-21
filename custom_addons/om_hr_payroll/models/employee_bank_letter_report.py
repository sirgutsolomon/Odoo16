# custom_addons/om_hr_payroll/models/employee_tax_report.py

from odoo import models, api

from datetime import datetime
class EmployeeBankLetterReport(models.AbstractModel):
    _name = 'report.om_hr_payroll.employee_bank_letter_report'
    _description = 'Employee Bank Letter Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        company = self.env.company
        currency = company.currency_id
        payslips = self.env['hr.payslip'].search([('state','=','done')])  # Get all employees or apply any filters as needed

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
            'company_branch':data.get('company_branch')
        }
