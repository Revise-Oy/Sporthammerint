# -*- coding: utf-8 -*-
from odoo import fields, models

class Website(models.Model):

    _inherit = "website"

    facebook_page_id = fields.Char(
        'Facebook Page ID', help='Page ID of the facebook account')
    facebook_access_token = fields.Char(
        'Facebook access Token',
        help='Token for the facebook account \
        URL to get Token:https://developers.facebook.com/tools/explorer')
    facebook_feed_limit = fields.Char(string="Feed Limit",required=True)
    fb_background_selection = fields.Selection([
        ('fb_background_image', 'Facebook Background Image'),
        ('fb_background_color', 'Facebook Background Color'),
    ])
    fb_background_image = fields.Binary("Facebook Background Image")
    custom_css = fields.Char(string="Custom css")
    fb_background_color = fields.Char("Facebook Background Color")




