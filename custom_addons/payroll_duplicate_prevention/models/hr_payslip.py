from odoo import models, api, _
from odoo.exceptions import ValidationError


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    @api.constrains('employee_id', 'date_from', 'date_to', 'state')
    def _check_duplicate_payslip(self):
        for payslip in self:
            if payslip.state == 'cancel':
                continue
            
            overlapping_payslips = self.search([
                ('employee_id', '=', payslip.employee_id.id),
                ('state', '!=', 'cancel'),
                ('id', '!=', payslip.id),
                '|',
                '&', ('date_from', '<=', payslip.date_from), ('date_to', '>=', payslip.date_from),
                '&', ('date_from', '<=', payslip.date_to), ('date_to', '>=', payslip.date_to),
            ])
            
            if overlapping_payslips:
                raise ValidationError(_(
                    "A payslip already exists for this employee during the selected period. "
                    "Please review existing payslips before creating a new one."
                ))

    @api.model_create_multi
    def create(self, vals_list):
        payslips = super().create(vals_list)
        payslips._check_duplicate_payslip()
        return payslips