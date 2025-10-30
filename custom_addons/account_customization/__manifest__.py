{
    'name': 'Account Customization',
    'version': '1.0',
    'category': 'Accounting/Accounting',
    'summary': 'Custom accounting modifications and enhancements',
    'description': """
        Custom accounting features and modifications based on business requirements.
    """,
    'author': 'Custom Development',
    'depends': ['account'],
    'data': [
        'views/account_payment_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}