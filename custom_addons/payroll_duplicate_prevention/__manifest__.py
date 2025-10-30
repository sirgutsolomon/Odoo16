{
    'name': 'Payroll Duplicate Prevention',
    'version': '0.1',
    'category': 'Human Resources/Payroll',
    'summary': 'Prevent duplicate payslip generation for same employee and period',
    'description': """
        Prevents HR/Payroll users from creating multiple payslips for the same employee
        within overlapping or identical date ranges to ensure data integrity.
    """,
    'author': 'Custom Development',
    'depends': ['om_hr_payroll'],
    'data': [],
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}