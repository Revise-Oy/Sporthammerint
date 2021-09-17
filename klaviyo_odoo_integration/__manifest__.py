{
    'name': 'Klaviyo Odoo Integration',
    'category': 'Marketing',
    'version': '14.01.06.2020',
    'summary': """""",
    'description': """ Using Kalviyo Integration We Import the Contacts,Campaign,Lists From Kaliyo To odoo.,We also provide omnisend,mailchamp,sendinblue marketing integration.""",

    'depends': ['sale', 'mass_mailing'],

    'data': [
        'security/ir.model.access.csv',
        'views/klaviyo_credential_details.xml',
        'views/klaviyo_list_details.xml'],

    'author': 'Vraja Technologies',
    'images': ['static/description/klaviyo.gif'],
    'maintainer': 'Vraja Technologies',
    'website': 'https://www.vrajatechnologies.com',
    'live_test_url': 'https://www.vrajatechnologies.com/contactus',
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'price': '111',
    'currency': 'EUR',
    'license': 'OPL-1',

}
