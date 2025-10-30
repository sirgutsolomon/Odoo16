from odoo import models, _
from odoo.exceptions import ValidationError


class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'

    def generate_payslips(self):
        # Check for duplicates before generating batch payslips
        for employee in self.slip_ids.mapped('employee_id'):
            existing_payslips = self.env['hr.payslip'].search([
                ('employee_id', '=', employee.id),
                ('state', '!=', 'cancel'),
                '|',
                '&', ('date_from', '<=', self.date_start), ('date_to', '>=', self.date_start),
                '&', ('date_from', '<=', self.date_end), ('date_to', '>=', self.date_end),
            ])
            
            if existing_payslips:
                raise ValidationError(_(
                    "A payslip already exists for employee %s during the selected period. "
                    "Please review existing payslips before creating new ones."
                ) % employee.name)
        
        return super().generate_pays