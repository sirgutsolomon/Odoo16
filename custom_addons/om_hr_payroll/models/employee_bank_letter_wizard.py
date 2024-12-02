from odoo import models, fields, api

class EmployeeBankLetterWizard(models.TransientModel):
    _name = 'employee.bank.letter.wizard'
    _description = 'Employee Bank Letter Wizard'

    bank_name = fields.Char(string="Bank Name",required=True)
    bank_branch = fields.Char(string="Bank Branch",required=True)
    company_bank_account = fields.Char(string="Company Bank Account",required=True)
    company_bank_account_branch = fields.Char(string="Company Bank Account Branch",required=True)
    company_branch = fields.Char(string="Company Branch",required=True)
    month = fields.Selection(
        selection=[
            ('01', 'January'),
            ('02', 'February'),
            ('03', 'March'),
            ('04', 'April'),
            ('05', 'May'),
            ('06', 'June'),
            ('07', 'July'),
            ('08', 'August'),
            ('09', 'September'),
            ('10', 'October'),
            ('11', 'November'),
            ('12', 'December'),
        ],
        string="Month",
        required=True
    )
    year = fields.Char(string="Year", required=True, default=lambda self: fields.Date.today().year)
    employee_branch = fields.Many2one(
        'hr.branch',
        string="Branch",
        required=False
    )
    def action_print_report(self):
        # Data to be passed to the report
        data = {
            'bank_name': self.bank_name,
            'bank_branch':self.bank_branch,
            'company_bank_account':self.company_bank_account,
            'company_bank_account_branch':self.company_bank_account_branch,
            'company_branch': self.company_branch,
            'year':self.year,
            'month':self.month,
            'branch_id': self.employee_branch.id,
        }
        # Call the report action for the HTML preview
        return self.env.ref('om_hr_payroll.action_employee_bank_letter').report_action(self, data=data)
