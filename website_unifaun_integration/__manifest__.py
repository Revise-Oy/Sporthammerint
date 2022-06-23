# -*- coding: utf-8 -*-pack
{
    # App information
    'name': 'Odoo eCommerce Unifaun Integration',
    'category': 'Website',
    'version': '14.0.03.12.2021',
    'summary': """""",
    'description': """ Unifaun Odoo Integration helps you integrate & manage your Unifaun account in odoo. manage your Delivery/shipping operations directly from odoo.provide the functionality of Get Rate,Export Orders,Generat Lable,Tracking. we also provide unifaun shipping integration,unifaun odoo integration,dhl express.""",

    'depends': [
        'website_sale',
        'website_sale_delivery',
        'unifaun_odoo_integration'
    ],

    'data': [
        'data/ir_config_parameter_data.xml',
        'templates/assests.xml',
        'templates/template.xml',
    ],

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
