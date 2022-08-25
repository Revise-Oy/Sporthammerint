# -*- coding: utf-8 -*-
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    unifaun_api_url = fields.Char(string='API URL', default='https://api.unifaun.com')
    unifaun_combine_id = fields.Char(string='Unifaun ID', help='Combine Id of your unifaun account')
    use_unifaun_integration = fields.Boolean(copy=False, string="Are You Use Unifaun Odoo Connector.?",
                                             help="If use Unifaun Integration than value set TRUE.",
                                             default=False)
