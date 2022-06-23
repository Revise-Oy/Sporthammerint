# -*- coding: utf-8 -*-pack
{

    # App information
    'name': 'Unifaun Odoo Integration',
    'category': 'Website',
    'version': '14.0.0',
    'summary': '',
    'description': """""",

    # Dependencies
    'depends': ['delivery'],

    # Views
    'data': [
        'security/ir.model.access.csv',
        'views/res_company.xml',
        'views/stock_picking.xml',
        'views/delivery_carrier.xml',
        'views/ir_actions_act_window.xml',
        'views/product_packaging.xml',
        'views/ir_ui_view.xml',
    ],

    # Author

    'author': 'Vraja Technologies',
    'website': 'http://www.vrajatechnologies.com',
    'maintainer': 'Vraja Technologies',
    'live_test_url': 'http://www.vrajatechnologies.com/contactus',
    'images': [''],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'price': '125',
    'currency': 'EUR',
    'license': 'OPL-1',

}

# version changelog
# 14.0.0 Initial version of the app
