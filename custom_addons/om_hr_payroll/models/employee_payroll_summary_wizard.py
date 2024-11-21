from odoo import models, fields, api

class EmployeeTaxReportWizard(models.TransientModel):
    _name = 'employee.payroll.summary.wizard'
    _description = 'Employee Tax Report Wizard'

    headoffice = fields.Char(string="Head Office")

    def action_print_report(self):
        # Data to be passed to the report
        data = {
            'headoffice': self.headoffice,
        }
        # Call the report action for the HTML preview
        return self.env.ref('om_hr_payroll.action_employee_payroll_summary').report_action(self, data=data)
