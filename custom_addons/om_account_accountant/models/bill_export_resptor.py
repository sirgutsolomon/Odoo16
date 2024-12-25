from odoo import models, fields

class AccountBillReportExport(models.TransientModel):
    _name = 'account.bill.report.excel'
    _description = 'Account Bill Report Excel Export'

    def action_export_excel(self):
        """Redirect to the export URL with filters."""
        url = f'/web/export/account_bill_export'
        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'new',
        }
