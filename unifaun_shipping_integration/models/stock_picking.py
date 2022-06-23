# -*- coding: utf-8 -*-
from .unifaun import Unifaun
from odoo import fields, models, _
from odoo.exceptions import ValidationError

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    unifaun_pickup_location_flag = fields.Boolean(related='carrier_id.create_shipment_pl_flag', copy=False)
    unifaun_pickup_address_ids = fields.One2many('unifaun.pickup.address', 'picking_id',
                                                 string="Unifaun Pickup Address")
    unifaun_pickup_address_id = fields.Many2one('unifaun.pickup.address', string='Unifaun Pickup Address', copy=False)


    def get_unifaun_pickup_location(self):
        if self.carrier_id and self.carrier_id.create_shipment_pl_flag == False:
            raise ValidationError(_('Please Enable Create Shipment Using Pickup Location Button In Delivery Carrier '))
        params = self.prepare_delivery_checkout_param()
        response_data = Unifaun.send_request(prepare_id=False, data=False,
                                             carrier_id=self.carrier_id, methods='GET',
                                             params=params, service='get_checkout')
        if response_data:
            wiz_id = self.set_data_pickup_location_wizard(response_data=response_data)
            action_data = self.env.ref(
                "unifaun_shipping_integration.action_unifaun_pickup_location"
            ).read()[0]
            action_data.update({'res_id': wiz_id.id})
            return action_data
        return self.env.ref(
            "unifaun_shipping_integration.action_unifaun_pickup_location"
        ).read()[0]

    def set_data_pickup_location_wizard(self, response_data):
        wiz_id = self.env['unifaun.pickup.location'].create({
            'picking_id': self.id
        })
        pickup_location_line = self.env['unifaun.pickup.location.line']
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
                                "wizard_id": wiz_id.id,
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
                                "agent_email": agent.get('email')

                            }
                            pickup_line = pickup_location_line.create(val)
                            pickup_location_line += pickup_line
                    else:
                        val = {
                            "wizard_id": wiz_id.id,
                            "carrier": carrier_id,
                            "shipping_provider": shipping_name,
                            "suboption_id": suboption_id,
                            "price": price_value,
                        }
                        pickup_line = pickup_location_line.create(val)
                        pickup_location_line += pickup_line
        wiz_id.wizard_line_ids += pickup_location_line
        return wiz_id

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


class UnifaunPickupLocation(models.TransientModel):
    _name = 'unifaun.pickup.location'
    _description = 'Unifaun Pickup Location Wizard'
    wizard_line_ids = fields.One2many('unifaun.pickup.location.line', 'wizard_id', string='Wizard Lines')
    picking_id = fields.Many2one('stock.picking', string='Stock')


class UnifaunPickupLocationLine(models.TransientModel):
    _name = 'unifaun.pickup.location.line'
    _description = 'Unifaun Pickup Location Line Wizard'

    wizard_id = fields.Many2one('unifaun.pickup.location', string='Wizard')
    carrier = fields.Char(string='Carrier')
    shipping_provider = fields.Char(string='Shipping provider')
    suboption_id = fields.Char(string='Id')
    price = fields.Char(string='Price')
    agent_name = fields.Char(string='Name')
    agent_address1 = fields.Char(string='Address1')
    agent_address2 = fields.Char(string='Address2')
    agent_zipCode = fields.Char(string='Zipcode')
    agent_city = fields.Char(string='City')
    agent_state = fields.Char(string='State')
    agent_country = fields.Char(string='Country')
    agent_phone = fields.Char(string='Phone')
    agent_email = fields.Char(string='Email')

    def set_receiver_address(self):
        picking_id = self.wizard_id and self.wizard_id.picking_id
        if picking_id.unifaun_pickup_address_ids:
            picking_id.unifaun_pickup_address_ids.unlink()
        vals = {
            "carrier": self.carrier,
            "shipping_provider": self.shipping_provider,
            "suboption_id": self.suboption_id,
            "price": self.price,
            "agent_name": self.agent_name,
            "agent_address1": self.agent_address1,
            "agent_address2": self.agent_address2,
            "agent_zipCode": self.agent_zipCode,
            "agent_city": self.agent_city,
            "agent_state": self.agent_state,
            "agent_country": self.agent_country,
            "agent_phone": self.agent_phone,
            "picking_id": picking_id.id
        }
        pickup_address_line = self.env['unifaun.pickup.address'].create(vals)
        picking_id.unifaun_pickup_address_id = pickup_address_line.id
        # picking_id.unifaun_pickup_address_ids += pickup_address_line
        return True
