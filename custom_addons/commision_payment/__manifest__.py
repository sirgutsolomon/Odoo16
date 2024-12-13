{
    'name': 'Commission Management',
    'version': '1.0',
    'summary': 'Manage driver payments and commission deductions',
    'category': 'Accounting',
    'author': 'fire fliar',
    'depends': ['base', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'views/commision_pay_view.xml',
        'views/actions.xml',
        'views/menu.xml',

    ],
    'installable': True,
    'application': True,
}
