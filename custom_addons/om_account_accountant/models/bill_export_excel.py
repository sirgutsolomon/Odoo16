import io
import xlsxwriter
from odoo import http
from odoo.http import content_disposition, request
from odoo.exceptions import UserError

class AccountBillExportExcel(http.Controller):
    @http.route('/web/export/account_bill_export', type='http', auth="user")
    def export_payslip_excel(self):
        # Create an Excel file
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet("Vednor Bill Report")
        bills = request.env['account.move'].sudo().search([
            ('move_type', '=', 'in_invoice'),
            ('state', '=', 'posted'),
        ])


        if not bills:
            raise UserError("No valid vendor bills selected.")

        # Prepare data for export
        data = []
        for bill in bills:
            partner = bill.partner_id
            taxable_amount = bill.amount_untaxed
            withholding_tax = taxable_amount * 0.02  # Assuming 2% withholding tax
            data.append({
                'Withholdee TIN': partner.vat or '',
                'Withholdee Full Name': partner.name or '',
                'Receipt No': bill.receipt_no,
                'Withhold Date': bill.invoice_date,
                'Total Taxable Amount': taxable_amount,
                'Tax Withheld': withholding_tax,
            })

        # Write headers
        headers = ['Withholdee TIN', 'Withholdee Full Name', 'Receipt No', 'Withhold Date',
                   'Total Taxable Amount', 'Tax Withheld']
        for col_num, header in enumerate(headers):
            worksheet.write(0, col_num, header)

        # Write data
        for row_num, record in enumerate(data, start=1):
            worksheet.write(row_num, 0, record['Withholdee TIN'])
            worksheet.write(row_num, 1, record['Withholdee Full Name'])
            worksheet.write(row_num, 2, record['Receipt No'])
            worksheet.write(row_num, 3, record['Withhold Date'])
            worksheet.write(row_num, 4, record['Total Taxable Amount'])
            worksheet.write(row_num, 5, record['Tax Withheld'])

        workbook.close()
        output.seek(0)
        # Return Excel file as response
        return request.make_response(
            output.read(),
            headers=[
                ('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
                ('Content-Disposition', content_disposition('Vendor_report_excel.xlsx'))
            ]
        )
