# -*- coding: utf-8 -*-pack
{
    # App information
    'name': 'Odoo eCommerce Unifaun Integration',
    'category': 'Website',
    'version': '15.0.21.06.2022',
    'summary': """""",
    'description': """Unifaun Odoo Integration helps you integrate & manage your Unifaun account in odoo. manage your 
    Delivery/shipping operations directly from odoo.provide the functionality of Get Rate,Export Orders,
    Generat Lable,Tracking. we also provide unifaun shipping integration,unifaun odoo integration,dhl express.""",

    'depends': [
        'website_sale',
        'website_sale_delivery',
        'unifaun_shipping_integration'
    ],

    'data': [
        'views/template.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'website_unifaun_integration/static/src/css/unifaun_shipping.css',
            'website_unifaun_integration/static/src/js/unifaun_shipping.js'
        ],
    },
    'author': 'Vraja Technologies',
    'maintainer': 'Vraja Technologies',
    'website': 'https://www.vrajatechnologies.com',
    'live_test_url': 'https://www.vrajatechnologies.com/contactus',
    'images': [],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'price': '25',
    'currency': 'EUR',
    'license': 'OPL-1',
}

# 15.0.21.06.2022
# initial version of the app
