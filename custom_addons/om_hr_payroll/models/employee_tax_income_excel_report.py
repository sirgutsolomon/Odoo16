from odoo import models, api
from datetime import datetime
import calendar

class EmployeeTaxIncomeReport(models.AbstractModel):
    _name = 'report.om_hr_payroll.employee_tax_income_report'
    _description = 'Employee Tax Income Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        # Extract data from wizard or controller
        selected_month = data.get('month')
        selected_year = data.get('year')
        branch_id = data.get('branch_id')

        # Calculate start and end dates
        start_date = f"{selected_year}-{selected_month}-01"
        last_day = calendar.monthrange(int(selected_year), int(selected_month))[1]
        end_date = f"{selected_year}-{selected_month}-{last_day}"
        url = f'/web/export/payslip_excel?month={selected_month}&year={selected_year}'
        if branch_id:
            url += f'&branch_id={branch_id.id}'

        # Search domain
        domain = [
            ('state', '=', 'done'),
            ('date_from', '>=', start_date),
            ('date_to', '<=', end_date)
        ]
        if branch_id:
            domain.append(('employee_id.employee_branch', '=', int(branch_id)))

        payslips = self.env['hr.payslip'].search(domain)

        # Group employees into pages
        report_pages = []
        current_page = []
        max_employees_per_page = 20  # Define the maximum number of employees per page

        for payslip in payslips:
            employee = payslip.employee_id
            employee_contract = employee.contract_id

            # Initialize fields
            transport_allowance = 0
            taxable_transport_allowance = 0
            over_time = 0
            other_taxable_benefit = 0
            total_taxable_income = 0
            tax_withheld = 0

            # Process payslip lines
            for line in payslip.line_ids:
                if line.code == 'Travel':
                    transport_allowance += int(line.total)
                if line.code == 'TAXABLETRANSPORTALLOWANCE':
                    taxable_transport_allowance += int(line.total)
                if line.category_id.name == "Taxable":
                    other_taxable_benefit += int(line.total)
                if line.category_id.name == "Taxable" and line.code != 'TAXABLETRANSPORTALLOWANCE':
                    total_taxable_income += int(line.total)
                if line.code == 'INCOMETAX':
                    tax_withheld += int(line.total)

            # Add employee data to the current page
            current_page.append({
                'employee_tin': employee.tin_number,
                'employee_name': employee.name,
                'contract_start_date': employee_contract.date_start.strftime('%d-%m-%Y'),
                'basic_salary': employee_contract.wage,
                'transport_allowance': transport_allowance,
                'taxable_transport_allowance': taxable_transport_allowance,
                'over_time': over_time,
                'other_taxable_benefit': other_taxable_benefit,
                'total_taxable_income': total_taxable_income,
                'tax_withheld': tax_withheld,
            })


            # Check if the current page is full
            if len(current_page) == max_employees_per_page:
                report_pages.append(current_page)
                current_page = []

        # Append remaining employees to the report
        if current_page:
            report_pages.append(current_page)

        # Additional metadata
        return {
            'company': self.env.company,
            'employees': report_pages,
            'month': selected_month,
            'year': selected_year,
            'url':url,
        }
