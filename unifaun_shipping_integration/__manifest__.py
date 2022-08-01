# -*- coding: utf-8 -*-pack
{
    # App information
    'name': 'Unifaun(nShift API) Shipping Integration',
    'category': 'Website',
    'version': '14.29.06.22',
    "summary": """Integrate & Manage Unifaun shipping operations from Odoo by using Odoo unifaun Integration.We are providing following modules odoo shipping integration,unifaun odoo shipping connector, dhl express, fedex, ups, gls, usps, stamps.com, shipstation, post.at,post-at,bigcommerce, easyship, sendclound,post.at austria shipping integration,colissimo,mrw,nacex.""",
    'live_test_url': 'http://www.vrajatechnologies.com/contactus',
    'depends': ['delivery'],
    # Views
    'data': [
        'security/ir.model.access.csv',
        'views/sale.xml',
        'views/res_company.xml',
        'views/stock_picking.xml',
        'views/delivery_carrier.xml',
        'views/ir_actions_act_window.xml',
        'views/product_packaging.xml',
        'views/ir_ui_view.xml',
    ],
    'images': ['static/description/cover.jpg'],
    'author': 'Vraja Technologies',
    'maintainer': 'Vraja Technologies',
    'website': 'www.vrajatechnologies.com',
    'demo': [],
    'live_test_url': 'https://www.vrajatechnologies.com/contactus',
    'installable': True,
    'application': True,
    'auto_install': False,
    'price': '279',
    'currency': 'EUR',
    'license': 'OPL-1',

}
# version changelog
# 14.0.0 Initial version of the app
# 14.0.1 add company field in delivery
# 14.0.17.11.2021 Latest version
# 14.0.18.11.2021 return configure carrier
# 14.0.25.11.2021 add receiver email or phone
# 14.0.26.11.2021 done for live


# 14.29.06.22
# Add new flow for delivery option
