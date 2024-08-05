# -*- coding: utf-8 -*-
{
    'name': "Custom Receipt",

    'summary': "Short (1 phrase/line) summary of the module's purpose",

    'description': """
Long description of module's purpose
    """,

    'author': "Cybernetics+",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Accounting',

    'version': '0.1',
    "installable": True,
    "application": False,
    "auto_install": False,
    # any module necessary for this one to work correctly
    'depends': ['base', 'account'],

    # always loaded
    'data': [
        'views/views.xml',
        # 'report/billing_template.xml',
        # 'report/billing_view.xml'
        # 'security/ir.model.access.csv',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}

