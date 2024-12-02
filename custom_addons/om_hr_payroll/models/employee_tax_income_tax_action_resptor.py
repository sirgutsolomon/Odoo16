from odoo import models
from odoo.http import request

# class HrPayslip(models.Model):
#     _inherit = 'hr.payslip'
#
#     def action_export_excel(self):
#         # Redirect to the controller
#         base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
#         return {
#             'type': 'ir.actions.act_url',
#             'url': f'{base_url}/web/export/payslip_excel',
#             'target': 'new',
#         }
from odoo import models, fields

class PayslipExportWizard(models.TransientModel):
    _name = 'employee.income.tax.excel.wizard'
    _description = 'Wizard for Exporting Payslips to Excel'

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
    year = fields.Char(
        string="Year",
        required=True,
        default=lambda self: fields.Date.today().year
    )
    employee_branch = fields.Many2one(
        'hr.branch',
        string="Branch",
        required=False
    )

    def action_export_excel(self):
        """Redirect to the export URL with filters."""
        url = f'/web/export/payslip_excel?month={self.month}&year={self.year}'
        if self.employee_branch:
            url += f'&branch_id={self.employee_branch.id}'
        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'new',
        }
