# -*- encoding: utf-8 -*-
{
    'name': 'Facebook Feed, Facebook Snippet in odoo',
    'category': 'Website',
    'version': '1.0',
    'summary': """
        Facebook Feed, Facebook Snippet, all your facebook post in your odoo website,  Facebook snippet in odoo, Facebook post in odoo, Website Facebook Feed in odoo 14, 13, 12, 11, 
        All your facebook post in odoo website with drag and drop snippet.""",
    'description': """
        Facebook Feed, Facebook Snippet, all your facebook post in your odoo website,  Facebook snippet in odoo, Facebook post in odoo, Website Facebook Feed in odoo 14, 13, 12, 11
    """,
    'depends': ['base', 'web', 'web_editor', 'website', ],
    'data': [
        'security/ir.model.access.csv',
        'views/res_config_settings.xml',
        'wizards/popup_wizard.xml',
        'wizards/popup_wizard_fail.xml',
        'views/snippets.xml',
    ],
    'price': 58.00,
    'currency': 'USD',
    'support': 'business@axistechnolabs.com',
    'author': 'Axis Technolabs',
    'website': 'http://www.axistechnolabs.com',
    'installable': True,
    'license': 'AGPL-3',
    'images': ['static/description/images/main_screenshot.png'],
    'live_test_url': 'https://youtu.be/QJqvcenBYJo', 
}
