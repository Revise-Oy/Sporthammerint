# -*- encoding: utf-8 -*-
from odoo.http import request
from odoo import http
import requests
import json

class main(http.Controller):

    @http.route(
        ['/facebook_id_token'], auth='public',type='json',
        website=True, csrf=False)
    def get_facebook_token(self, **kwargs):

        website = request.website
        if not website:
            website = request.env.ref('website.default_website')
            website = website
        facebook_page_id = request.website.facebook_page_id
        facebook_access_token = request.website.facebook_access_token
        facebook_feed_limit = request.website.facebook_feed_limit
        fb_background_selection = request.website.fb_background_selection
        fb_background_image = request.website.fb_background_image
        fb_background_color = request.website.fb_background_color
        custom_css = request.website.custom_css

        post = 'https://graph.facebook.com/v8.0/%s' % (website.facebook_page_id)
        post_url = '%s?fields=posts.limit(%s){permalink_url,status_type,id,message,full_picture,icon,created_time,from,shares,comments,likes,attachments{media,url}}&access_token=%s' % (
            post,website.facebook_feed_limit, website.facebook_access_token)
        res = requests.request(url=post_url, method="GET")
        result=requests.get(post_url).json()
        image_url = 'https://graph.facebook.com/v8.0/%s/picture' % (website.facebook_page_id)
        response = {
                "fb_result" : result,
                "fb_page_id" : facebook_page_id,
                "fb_image_url" : image_url,
                'fb_background_selection':fb_background_selection,
                'fb_background_image':fb_background_image,
                'fb_background_color':fb_background_color,
                'custom_css':custom_css,
        }
        if res.ok or res.status_code == 200:
            if "next" in result['posts']['paging']:
                request.session['val_name'] = result['posts']['paging']['next']
            else:
                request.session['val_name'] = ''
        else:
            request.session['val_name'] = ''
        return response
        
    @http.route(
        ['/facebook_post_next'], auth='public',type='json',
        website=True, csrf=False)
    def get_next_post(self, **kwargs): 
        if request.httprequest.method == 'POST':
            website = request.website
            if not website:
                website = request.env.ref('website.default_website')
                website = website
            if request.session['val_name']:
                page_number = kwargs.get('page_number') 
                post_url = request.session['val_name']
                res = requests.request(url=post_url, method="GET")
                result=requests.get(post_url).json()
                facebook_page_id = request.website.facebook_page_id
                image_url = 'https://graph.facebook.com/v8.0/%s/picture' % (website.facebook_page_id)
                response = {
                    "fb_result" : result,
                    "fb_page_id" : facebook_page_id,
                    "fb_image_url" : image_url
                }
                if res.ok or res.status_code == 200:
                    if "next" in result['paging']:
                        request.session['val_name'] = result['paging']['next']
                    else:
                        request.session['val_name'] = ''
                return response
            else:
                return 0
        else:
            return 0


