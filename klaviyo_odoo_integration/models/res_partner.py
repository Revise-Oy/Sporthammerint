from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError, Warning

class ResPartner(models.Model):
    _inherit = "res.partner"
    klaviyo_list_id = fields.Many2one('klaviyo.list.details',string="Klaviyo List")
    exported_in_klaviyo = fields.Boolean(copy=False, string="Exported In Klaviyo",default=False)
