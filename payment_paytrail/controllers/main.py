# -*- coding: utf-8 -*-
# Part of Kanak Infosystems LLP. See LICENSE file for full copyright and licensing details.

import logging
import pprint
import werkzeug

from odoo import http
from odoo.http import request, Response

_logger = logging.getLogger(__name__)


class PaytrailController(http.Controller):
    _return_url = '/payment/paytrail/success/'
    _cancel_url = '/payment/paytrail/cancel/'
    _notify_url = '/payment/paytrail/notify/'

    @http.route([_return_url, _cancel_url], type='http', auth='public', csrf=False)
    def paytrail_form_feedback(self, **post):
        _logger.info('Paytrail: entering form_feedback with post data %s', pprint.pformat(post))
        request.env['payment.transaction'].sudo().form_feedback(post, 'paytrail')
        return werkzeug.utils.redirect('/payment/process')

    @http.route(_notify_url, type='http', auth='public', csrf=False)
    def paytrail_notify_form_feedback(self, **post):
        _logger.info('Paytrail: getting post data with notify url %s', pprint.pformat(post))
        tx = request.env['payment.transaction'].sudo().search([('reference', '=', post.get('ORDER_NUMBER'))])
        if tx.state != 'done':
            request.env['payment.transaction'].sudo().form_feedback(post, 'paytrail')
            return werkzeug.utils.redirect('/payment/process')
        return Response("OK", status=200)
