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


class PosConfig(models.Model):
    _inherit = 'pos.config'

    nets_terminal_id = fields.Char(string="Nets payment terminal id")
    nets_payment_active = fields.Boolean(compute='_compute_nets_payment_active')

    @api.depends('payment_method_ids')
    def _compute_nets_payment_active(self):
        for config in self:
            nets = config.mapped('payment_method_ids').filtered(lambda p: p.use_payment_terminal == 'nets_cloud')
            config.nets_payment_active = True if nets else False
