import io
import xlsxwriter
from odoo import http
from odoo.http import content_disposition, request

class PayslipExportController(http.Controller):
    @http.route('/web/export/payslip_excel', type='http', auth="user")
    def export_payslip_excel(self, **kwargs):
        # Create an Excel file
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet("Payslip Report")

        # Add headers
        bold = workbook.add_format({'bold': True})
        sheet.write(0, 0, "Employee Tin", bold)
        sheet.write(0, 1, "Employee Name", bold)
        # don't forget to find the earliest contract start date
        sheet.write(0, 2, "Start Date", bold)
        sheet.write(0, 3, "End Date", bold)
        sheet.write(0, 4, "Basic Salary", bold)
        sheet.write(0, 5, "Transport Allowance", bold)
        sheet.write(0, 6, "Taxable Transport Allowance", bold)
        sheet.write(0, 7, "Over Time", bold)
        sheet.write(0, 8, "Other Taxable Benefit", bold)
        sheet.write(0, 9, "Total Taxable Income", bold)
        sheet.write(0, 10, "Tax Withheld", bold)
        sheet.write(0, 11, "Cost Sharing", bold)

        month = kwargs.get('month')
        year = kwargs.get('year')
        branch_id = kwargs.get('branch_id')
        if not month or not year:
            return request.not_found()

        # Calculate start and end dates for the selected month
        import calendar
        last_day = calendar.monthrange(int(year), int(month))[1]
        start_date = f"{year}-{month}-01"
        end_date = f"{year}-{month}-{last_day}"
        domain = [('state', '=', 'done'),
                  ('date_from', '>=', start_date),
                  ('date_to', '<=', end_date), ]
        if branch_id:
            domain.append(('employee_id.employee_branch', '=', int(branch_id)))
        payslips = request.env['hr.payslip'].search(domain)
        row = 1
        for payslip in payslips:
            employee_info = payslip.employee_id
            employee_contract = employee_info.contract_id
            sheet.write(row, 0, employee_info.tin_number)
            sheet.write(row, 1, employee_info.name)
            sheet.write(row, 2, employee_contract.date_start)
            # No thrid column
            sheet.write(row, 4, employee_contract.wage)
            transport_allowance = 0
            taxable_transport_allowance = 0
            other_taxable_benefit = 0
            total_taxable_income = 0
            tax_witheld = 0

            for line in payslip.line_ids:
                if (line.code == 'Travel'):
                    transport_allowance += int(line.total)
                if (line.code == 'TAXABLETRANSPORTALLOWANCE'):
                    taxable_transport_allowance += int(line.total)
                if line.category_id.name == "Taxable":
                    other_taxable_benefit += int(line.total)
                if line.category_id.name == "Taxable" and line.code != 'TAXABLETRANSPORTALLOWANCE':
                    total_taxable_income += int(line.total)
                if (line.code == 'INCOMETAX'):
                    tax_witheld += int(line.total)
            sheet.write(row, 5, transport_allowance)
            sheet.write(row, 6, taxable_transport_allowance)
            sheet.write(row, 8, other_taxable_benefit)
            sheet.write(row, 9, total_taxable_income)
            sheet.write(row, 10, tax_witheld)
            row += 1

        workbook.close()
        output.seek(0)

        # Return Excel file as response
        return request.make_response(
            output.read(),
            headers=[
                ('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
                ('Content-Disposition', content_disposition('Payslip_Report.xlsx'))
            ]
        )
