# -*- coding: utf-8 -*-
#################################################################################
# Author      : Kanak Infosystems LLP. (<https://www.kanakinfosystems.com/>)
# Copyright(c): 2012-Present Kanak Infosystems LLP.
# All Rights Reserved.
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://www.kanakinfosystems.com/license>
#################################################################################

{
    'name': 'Paytrail Payment Acquirer',
    'version': '1.2',
    'category': 'Accounting/Payment Acquirers',
    'summary': '''
Paytrail payment gateway supports only EUR currency. This module contains both E1 and E2 version of paytrail payment gateway
Nordea | Osuuspankki | Danske Bank | Ålandsbanken (Bank of Åland) | Alandsbanken (Bank of Aland) | Handelsbanken | PayPal | S-Pankki | Jousto | Aktia | POP Pankki | Säästöpankki (Savings Banks Group) | Saastopankki (Savings Banks Group) | Visa (Nets) | MasterCard (Nets) | Diners Club (Nets) | American Express (Nets) | MobilePay | Collector Bank | Oma Säästöpankki | Oma Saastopankki
    ''',
    'description': """
        Paytrail: Payment Gateway
        Paytrail payment gateway supports only EUR currency
        This module contains both E1 and E2 version of paytrail payment gateway
    """,
    'license': 'OPL-1',
    'author': 'Kanak Infosystems LLP.',
    'website': 'https://www.kanakinfosystems.com',
    'depends': ['payment'],
    'images': ['static/description/banner.jpg'],
    'data': [
        'views/payment_acquirer_views.xml',
        'views/payment_acquirer_templates.xml',
        'data/payment_acquirer_data.xml',
    ],
    'sequence': 1,
    'installable': True,
    'price': 50,
    'currency': 'EUR',
    'post_init_hook': 'create_missing_journal_for_acquirers',
    'uninstall_hook': 'uninstall_hook',
}
