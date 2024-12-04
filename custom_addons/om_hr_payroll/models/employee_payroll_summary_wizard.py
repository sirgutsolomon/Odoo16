from odoo import models, fields, api

class EmployeeTaxReportWizard(models.TransientModel):
    _name = 'employee.payroll.summary.wizard'
    _description = 'Employee Tax Report Wizard'

    headoffice = fields.Char(string="Head Office", required=True)
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
            'headoffice': self.headoffice,
            'month':self.month,
            'year':self.year,
            'branch_id':self.employee_branch.id,
        }
        # Call the report action for the HTML preview
        return self.env.ref('om_hr_payroll.action_employee_payroll_summary').report_action(self, data=data)
