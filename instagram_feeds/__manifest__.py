# -*- encoding: utf-8 -*-
{
    'name': 'Instagram Feed Snippet, Instagram posts display in odoo website',
    'category': 'Website',
    'version': '14.0',
    'summary': 'Responsive instgram feed snippet, Instagram posts display in odoo website '
    'supported in Odoo v10, v11, v12, v13, v14',
    'description': """
        Responsive instgram feed snippet, Instagram posts display in odoo website
        supported in Odoo v10, v11, v12, v13, v14
    """,
    'depends': ['base', 'web', 'web_editor', 'website', ],
    'data': [
        'views/res_config_settings_views.xml',
        'views/snippets.xml',
    ],
    'demo': [],
    'price': 44.00,
    'currency': 'USD',
    'support': 'business@axistechnolabs.com',
    'author': 'Axis Technolabs',
    'website': 'http://www.axistechnolabs.com',
    'installable': True,
    'license': 'OPL-1',
    'images': ['static/description/images/main_screenshot.png'],
}
