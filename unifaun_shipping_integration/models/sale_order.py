import requests

from odoo import fields, models, _
from .unifaun import Unifaun
from odoo.exceptions import ValidationError
from odoo.addons.iap import jsonrpc, InsufficientCreditError

DEFAULT_ENDPOINT =  'https://iap-sandbox.odoo.com/' #'https://iap.sandbox.odoo.unifaun.com/'


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    unifaun_pickup_location_flag = fields.Boolean(related='carrier_id.create_shipment_pl_flag', copy=False)
    unifaun_location_ids = fields.One2many('unifaun.pickup.address', 'sale_id', string='Unifaun Pickup Location')
    unifaun_location_id = fields.Many2one('unifaun.pickup.address', string='Pickup Location', copy=False)

    def prepare_delivery_checkout_param(self):
        company_id = self.carrier_id and self.carrier_id.company_id
        currency = company_id and company_id.currency_id and company_id.currency_id.name
        to_country = self.partner_id and self.partner_id.country_id and self.partner_id.country_id.code
        to_zip = self.partner_id and self.partner_id.zip
        params = {
            "currency": currency,
            "language": "en",
            "tocountry": to_country,
            "tozipcode": to_zip,
        }
        return params

    def get_uni_pickup_location(self):
        """
        get all pickup location from unifaun and snd set into odoo sale order
        """
        # check for iap
        user_token = self.env['iap.account'].get('unifaun_odoo')
        params = self.prepare_delivery_checkout_param()
        response_data = Unifaun.send_request(prepare_id=False, data=False,
                                             carrier_id=self.carrier_id, methods='GET',
                                             params=params, service='get_checkout')
        if response_data:
            # remove old record
            old_rec = self.env['unifaun.pickup.address'].search([('sale_id', '=', self.id)])
            if old_rec:
                old_rec.sudo().unlink()
            self.save_pickup_location(response_data=response_data)
        return True

    def save_pickup_location(self, response_data):
        unifaun_obj = self.env['unifaun.pickup.address']
        for option in response_data.get('options'):
            option_id = option and option.get('id')
            delivery_option_id = self.carrier_id and self.carrier_id.carrier_delivery_option_id

            # if option id delivery option id are same then create record
            if option_id == delivery_option_id:
                shipping_name = option and option.get('name')
                suboption = option and option.get('subOptions')
                for sub in suboption:
                    carrier_id = sub.get('carrierId')
                    price_value = sub.get('priceValue')
                    service_id = sub.get('serviceId')
                    suboption_id = sub.get('id')
                    agent_locations = sub.get('agents')
                    if agent_locations:
                        for agent in agent_locations:
                            agent_id = agent.get('id')
                            val = {
                                "carrier": carrier_id,
                                "shipping_provider": shipping_name,
                                "suboption_id": suboption_id,
                                "price": price_value,
                                "agent_name": agent.get('name'),
                                "agent_address1": agent.get('address1'),
                                "agent_address2": agent.get('address2'),
                                "agent_zipCode": agent.get('zipCode'),
                                "agent_city": agent.get('city'),
                                "agent_state": agent.get('state'),
                                "agent_country": agent.get('country'),
                                "agent_phone": agent.get('phone'),
                                "agent_email": agent.get('email'),
                                "sale_id": self.id

                            }
                            unifaun_obj.create(val)
                    else:
                        val = {
                            "carrier": carrier_id,
                            "shipping_provider": shipping_name,
                            "suboption_id": suboption_id,
                            "price": price_value,
                        }
                        unifaun_obj.create(val)
        return True
