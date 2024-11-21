from odoo import models, fields, api

class EmployeeBankLetterWizard(models.TransientModel):
    _name = 'employee.bank.letter.wizard'
    _description = 'Employee Bank Letter Wizard'

    bank_name = fields.Char(string="Bank Name")
    bank_branch = fields.Char(string="Bank Branch")
    company_bank_account = fields.Char(string="Company Bank Account")
    company_bank_account_branch = fields.Char(string="Company Bank Account Branch")
    company_branch = fields.Char(string="Company Branch")





    def action_print_report(self):
        # Data to be passed to the report
        data = {
            'bank_name': self.bank_name,
            'bank_branch':self.bank_branch,
            'company_bank_account':self.company_bank_account,
            'company_bank_account_branch':self.company_bank_account_branch,
            'company_branch': self.company_branch,

        }
        # Call the report action for the HTML preview
        return self.env.ref('om_hr_payroll.action_employee_bank_letter').report_action(self, data=data)
