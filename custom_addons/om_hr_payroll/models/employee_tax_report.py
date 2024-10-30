from odoo import models, api

class EmployeeTaxReport(models.AbstractModel):
    _name = 'report.custom_employee_tax_report.report_employee_tax_template'

    @api.model
    def _get_report_values(self, docids, data=None):
        # Fetch the current company (you can adjust this to fetch any specific company if needed)
        company = self.env.company
        employees = self.env['hr.employee'].search([])  # Get all employees
        count = 1
        employee_tax_data = []
        current_batch = []

        for employee in employees:
            contract = employee.contract_id  # Get the employee's contract
            current_batch.append({
                "no": count,
                'tin_number': employee.tin_number,
                'name': employee.legal_name,
                'start_date': employee.first_contract_date,
                'basic_salary': contract.wage,
                'transport_allowance': contract.travel_allowance,
                'taxable_transport_allowance': "",  # Adjust this as needed
                'over_time': "",
                'other_taxable_benefits': contract.meal_allowance + contract.medical_allowance + contract.other_allowance,
                'taxable_income': "",
                'tax_withheld': "",
                'cost_sharing': "",
                'net_payment': ""
            })

            count += 1

            # If the current batch reaches 20, append it to employee_tax_data and reset
            if len(current_batch) == 1:
                employee_tax_data.append(current_batch)
                current_batch = []  # Reset the current batch

        # Append any remaining employees in the last batch
        if current_batch:
            employee_tax_data.append(current_batch)

        return {
            'company': company,  # Pass the real company object
            'employees': employee_tax_data,  # Pass employee info as an array of arrays
        }