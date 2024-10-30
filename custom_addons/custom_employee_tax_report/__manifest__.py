{
    'name': 'Employee Tax Report',
    'version': '1.0',
    'category': 'HR',
    'description': 'A custom module to generate employee tax reports',
    'author': 'Fairfax Solutions',
    'depends': ['base', 'hr', 'web'],  # hr for employee data
    'data': [
        'reports/report_action.xml',  # Action to render the reports
        "reports/employee_tax_report_template.xml",
        'views/report_menu.xml',  # Menu item for reports access
    ],
    'installable': True,
    'application': True,
}
