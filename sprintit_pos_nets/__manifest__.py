# -*- coding: utf-8 -*-
##############################################################################
#
#    ODOO Open Source Management Solution
#
#    ODOO Addon module by Sprintit Ltd
#    Copyright (C) 2021 Sprintit Ltd (<http://sprintit.fi>).
#
##############################################################################

{
    'name': 'SprintIT POS Nets Connect@Cloud',
    'version': '13.0',
    'license': 'Other proprietary',
    'category': 'Point Of Sale',
    'description': 'SprintIT POS Nets Connect@Cloud payment terminal integration',
    'author': 'SprintIT, Johan Tötterman',
    'maintainer': 'SprintIT, Johan Tötterman',
    'website': 'http://www.sprintit.fi',
    'depends': [
        'point_of_sale',
    ],
    'data': [
        'views/pos_payment_method_views.xml',
        'views/point_of_sale_assets.xml',
        'views/pos_config_views.xml',
    ],
    'demo': [
    ],
    'test': [
    ],
    "external_dependencies": {
    },
    'installable': True,
    'auto_install': False,
 }
