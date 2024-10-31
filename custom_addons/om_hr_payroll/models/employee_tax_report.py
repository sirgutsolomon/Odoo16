from odoo import models, api
from datetime import date
import calendar
class EmployeeTaxReport(models.AbstractModel):
    _name = 'report.om_hr_payroll.report_employee_tax_template'

    @api.model
    def _get_report_values(self, docids, data=None):
        company = self.env.company
        employees = self.env['hr.employee'].search([])  # Get all employees
        count = 1
        employee_tax_data = []
        current_batch = []
        end_date_employee = []
        month = ''
        year = ''
        first_payslip_date = None
        end_of_month_date = None
        if employees:
            for employee in employees:
                payslips = self.env['hr.payslip'].search([('employee_id', '=', employee.id)], limit=1,
                                                        order='date_from ASC')
                if payslips:
                    first_payslip_date = payslips.date_from
                    month = first_payslip_date.strftime('%b').upper()  # E.g., "FEB", "NOV"
                    year = first_payslip_date.strftime('%Y')
                    break
                else:
                    print("No payslips found for the first employee.")

        for employee in employees:
            contract = employee.contract_id  
            if(contract.date_end and contract.date_end.strftime('%b').upper() == month and contract.date_end.strftime('%Y') == year):
                end_date_employee.append({
                    "no": count,
                    'tin_number': employee.tin_number,
                    'name': employee.legal_name,
                })

            current_batch.append({
                "no": count,
                'tin_number': employee.tin_number,
                'name': employee.legal_name,
                'start_date': employee.first_contract_date,
                'basic_salary': contract.wage,
                'transport_allowance': contract.travel_allowance,
                'taxable_transport_allowance': "",  
                'over_time': "",
                'other_taxable_benefits': contract.meal_allowance + contract.medical_allowance + contract.other_allowance,
                'taxable_income': "",
                'tax_withheld': "",
                'cost_sharing': "",
                'net_payment': ""
            })

            count += 1

            if len(current_batch) == 7:
                employee_tax_data.append(current_batch)
                current_batch = []  

        if current_batch:
            employee_tax_data.append(current_batch)
        if(first_payslip_date):
            last_day = calendar.monthrange(first_payslip_date.year, first_payslip_date.month)[1]
            end_of_month_date = date(first_payslip_date.year, first_payslip_date.month, last_day).strftime('%d-%m-%Y')

        return {
            'company': company,  
            'employees': employee_tax_data,  
            'month': month,
            'year':year,
            'end_date_employee':end_date_employee,
            'first_payslip_date':first_payslip_date,
            'end_of_month_date':end_of_month_date
        }