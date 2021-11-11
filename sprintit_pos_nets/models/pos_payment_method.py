# -*- coding: utf-8 -*-
##############################################################################
#
#    ODOO Open Source Management Solution
#
#    ODOO Addon module by Sprintit Ltd
#    Copyright (C) 2021 Sprintit Ltd (<http://sprintit.fi>).
#
##############################################################################

import json
import logging
import pprint
import random
import requests
import string

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class PosPaymentMethod(models.Model):
    _inherit = 'pos.payment.method'

    def _get_payment_terminal_selection(self):
        return super(PosPaymentMethod, self)._get_payment_terminal_selection() + [('nets_cloud', 'Nets Connect@Cloud')]

    nets_api_url = fields.Char(string="Nets Cloud API URL")
    nets_username = fields.Char(string="Nets username")
    nets_password = fields.Char(string="Nets password")
    nets_api_token = fields.Char(string="Nets API Token", copy=False)

    def _is_write_forbidden(self, fields):
        whitelisted_fields = {'nets_api_token'}
        return super(PosPaymentMethod, self)._is_write_forbidden(fields - whitelisted_fields)

    @api.onchange('use_payment_terminal')
    def _onchange_use_payment_terminal(self):
        super(PosPaymentMethod, self)._onchange_use_payment_terminal()
        if self.use_payment_terminal != 'nets_cloud':
            self.nets_api_token = False

    @api.model
    def set_nets_api_token(self, payment_method_id, api_token):
        payment_method = self.sudo().browse(payment_method_id)
        payment_method.nets_api_token = api_token

