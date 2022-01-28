# -*- encoding: utf-8 -*-
from odoo.http import request
from odoo import http
import requests
import json


class main(http.Controller):

    @http.route(
        ['/instagram_id_token'], type='json', auth='public',
        website=True, csrf=False)
    def get_instagram_token(self, **kwargs):
        website = request.website
        if not website:
            website = request.env.ref('website.default_website')
            website = website
        instagram_user_id = website.instagram_user
        instagram_token = website.instagram_token
        instagram_feed_limit = request.website.instagram_feed_limit
        post = 'https://graph.instagram.com/me'
        post_url = '%s/media?fields=media_url,permalink,media_type,thumbnail_url,username,caption,like_count,comments_count,timestamp&access_token=%s&limit=%s' % (
            post, website.instagram_token,website.instagram_feed_limit)
        res = requests.request(url=post_url, method="GET")
        if res.status_code != 400:
            result=requests.get(post_url).json()
        else:
            result = {}
        #image_url_request = 'https://graph.facebook.com/v10.0/%s?fields=profile_picture_url&access_token=%s' % (website.instagram_user, website.instagram_token)
        #image_url=requests.get(image_url_request).json()
        #image_url = 'https://www.axistechnolabs.com/images/logo.png'
        responce = {
                "result" : result,
                #"image_url" : image_url,
        }
        if res.ok or res.status_code == 200:
            if "next" in result['paging']:
                request.session['val_name'] = result['paging']['next']
            else:
                request.session['val_name'] = ''
        else:
            request.session['val_name'] = ''

        return responce

    @http.route(
        ['/instagram_post_next'], auth='public',type='json',
        website=True, csrf=False)
    def get_next_post(self, **kwargs):
        if request.httprequest.method == 'POST':
            website = request.website
            if not website:
                website = request.env.ref('website.default_website')
                website = website

            page_number = kwargs.get('page_number')
            post_url = request.session['val_name']
            if request.session['val_name']:
                res = requests.request(url=post_url, method="GET")
                result=requests.get(post_url).json()
                #image_url_request = 'https://graph.facebook.com/v10.0/%s?fields=profile_picture_url&access_token=%s' % (website.instagram_user, website.instagram_token)
                #image_url=requests.get(image_url_request).json()
                #image_url = 'https://www.axistechnolabs.com/images/logo.png'
                responce = {
                    "result" : result,
                    #"image_url" : image_url,
                }
                if res.ok or res.status_code == 200:
                    if "next" in result['paging']:
                        request.session['val_name'] = result['paging']['next']
                    else:
                        request.session['val_name'] = ''
                return responce
            else:
                return 0
        else:
            return 0
