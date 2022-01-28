# -*- coding: utf-8 -*-
import requests
from odoo import fields, models, _
from odoo.exceptions import UserError


class ResConfigSettings(models.TransientModel):

    _inherit = 'res.config.settings'

    instagram_user = fields.Char(
        'Instagram UserID',
        related='website_id.instagram_user', readonly=False)
    instagram_token = fields.Char(
        'Instagram Token',
        related='website_id.instagram_token', readonly=False)
    instagram_feed_limit = fields.Char('Feed Limit',related='website_id.instagram_feed_limit',readonly=False,required=True)

    def test_instagram_api_connection(self):
        self.ensure_one()
        if not self.instagram_user:
            raise UserError(_("Please configure USERID."))
        if not self.instagram_token:
            raise UserError(_("Please configure Token."))
        user = 'https://graph.facebook.com/%s' % (self.instagram_user)
        full_link = '%s/media?fields=media_url,permalink,media_type,thumbnail_url,username,caption,like_count,comments_count&access_token=%s' % (
            user, self.instagram_token)
        res = requests.request(url=full_link, method="GET")
        if res.ok or res.status_code == 200:
            raise UserError(_("Connection test success."))
        else:
            raise UserError(_("Connection test failed."))
