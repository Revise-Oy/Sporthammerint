# -*- coding: utf-8 -*-
from odoo import fields, models


class Website(models.Model):

    _inherit = "website"

    instagram_user = fields.Char(
        'Instagram UserID', help='User ID of the instagram account')
    instagram_token = fields.Char(
        'Instagram Token',
        help='Token for the instagram account \
        URL to get Token:http://instagram.pixelunion.net/')
    instagram_feed_limit = fields.Char(string="Feed Limit", required=True)
