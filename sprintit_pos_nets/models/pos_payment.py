# -*- coding: utf-8 -*-
##############################################################################
#
#    ODOO Open Source Management Solution
#
#    ODOO Addon module by Sprintit Ltd
#    Copyright (C) 2021 Sprintit Ltd (<http://sprintit.fi>).
#
##############################################################################

from odoo import fields, models, api, _


class PoSPayment(models.Model):
    _inherit = "pos.payment"

    nets_payment_response = fields.Text(string='Nets Payment Response')

    @api.model
    def set_nets_api_token(self, payment_method_id, api_token):
        payment_method = self.sudo().browse(payment_method_id)
        payment_method.nets_api_token = api_token
