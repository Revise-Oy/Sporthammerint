# -*- coding: utf-8 -*-
from odoo import fields, models


class PickupAddress(models.Model):
    _name = 'unifaun.pickup.address'
    _description = "Unifaun Pickup Address Details"

    shipping_provider = fields.Char(string='Shipping Provider')
    carrier = fields.Char(string='Carrier')
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

    picking_id = fields.Many2one('stock.picking', string='Stock')
