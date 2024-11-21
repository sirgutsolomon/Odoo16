from odoo import models
from odoo.http import request

class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    def action_export_excel(self):
        # Redirect to the controller
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        return {
            'type': 'ir.actions.act_url',
            'url': f'{base_url}/web/export/payslip_excel',
            'target': 'new',
        }
