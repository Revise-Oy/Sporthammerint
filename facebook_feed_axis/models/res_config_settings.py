import requests
from odoo import models, fields, api,_
from odoo.exceptions import UserError

class ResConfigSettings(models.TransientModel):

    _inherit = 'res.config.settings'

    facebook_page_id = fields.Char(
        'Facebook PageID',
        related='website_id.facebook_page_id', readonly=False)
    facebook_access_token = fields.Char(
        'Facebook Token',
        related='website_id.facebook_access_token', readonly=False)
    # test_connection = fields.Boolean(string='Test API Connection')
    facebook_feed_limit = fields.Char('Feed Limit',related='website_id.facebook_feed_limit',readonly=False,required=True)
    fb_background_selection = fields.Selection([
        ('fb_background_image', 'Facebook Background Image'),
        ('fb_background_color', 'Facebook Background Color'),
    ],related="website_id.fb_background_selection",readonly=False)
    fb_background_image = fields.Binary("Facebook Background Image",related="website_id.fb_background_image",readonly=False)
    custom_css = fields.Char(string="Custom css",readonly=False,related='website_id.custom_css')
    fb_background_color = fields.Char("Facebook Background Color",related="website_id.fb_background_color",readonly=False)
    

    def test_facebook_api_connection(self):
        self.ensure_one()
        if not self.facebook_page_id:
            raise UserError(_("Please configure pageID."))
        if not self.facebook_access_token:
            raise UserError(_("Please configure Token."))
        user = 'https://graph.facebook.com/%s' % (self.facebook_page_id)
        full_link = '%s?fields=id,name&access_token=%s' % (
            user, self.facebook_access_token)
        res = requests.request(url=full_link, method="GET")   
        if res.ok or res.status_code == 200:
            return {
                'name' : _('Success'),
                'type': 'ir.actions.act_window',
                'res_model': 'popup.wizard',
                'view_mode': 'form',
                'view_type': 'form',
                'views': [(False, 'form')],
                'target': 'new',
             }
        else:
            return {
                'name' : _('Fail'),
                'type': 'ir.actions.act_window',
                'res_model': 'popup.wizard.fail',
                'view_mode': 'form',
                'view_type': 'form',
                'views': [(False, 'form')],
                'target': 'new',
             }

