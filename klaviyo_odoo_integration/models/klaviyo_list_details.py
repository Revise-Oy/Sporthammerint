import base64
import json
from datetime import datetime
from requests import request
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError, Warning
import logging

_logger = logging.getLogger(__name__)


class klaviyoListDetails(models.Model):
    _name = "klaviyo.list.details"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char("Name", required=True, help="klaviyo List")
    klaviyo_list_type = fields.Selection([('segment', 'Segment'), ('list', 'list')], string="klaviyo list Type")
    klaviyo_id = fields.Char("Klaviyo ID", help="klaviyo ID")
    klavio_customer_ids = fields.One2many('klaviyo.customer.details', 'klaviyo_list_id', string="Customers")

    def klaviyo_to_odoo_import_lists(self, credential_id=False):
        api_url = credential_id.making_klaviyo_url("/api/v2/lists?api_key=%s" % (credential_id.klaviyo_api_key))
        response_data = credential_id.api_calling_function(api_url)
        if response_data.status_code != 200:
            raise ValidationError("Error Code : %s - %s" % (response_data.status_code, response_data.reason))
        response_datas = response_data.json()
        if isinstance(response_datas, dict):
            response_datas = [response_datas]
        for list in response_datas:
            name = list.get('list_name')
            list_id = list.get('list_id')
            if not self.search([('klaviyo_id', '=', list_id), ('klaviyo_list_type', '=', 'list')]):
                self.create({'name': name, 'klaviyo_list_type': 'list', 'klaviyo_id': list_id})


    def export_list_from_odoo_to_klaviyo(self):
        credential_id = self.env['klaviyo.credential.details'].search([], limit=1)
        if not credential_id:
            raise ValidationError("Credentials not available!")
        request_data = {
                "api_key": credential_id.klaviyo_api_key,
                "list_name": "%s"%(self.name),
            }
        data = json.dumps(request_data)
        api_url = "%s/api/v2/lists" % (credential_id.klaviyo_api_url)
        _logger.info("Request Data: %s" % (data))
        headers = {'Content-Type': 'application/json'}
        try:
            response_data = request(method='POST', url=api_url, data=data, headers=headers)
        except Exception as e:
            raise ValidationError(e)

        if response_data.status_code != 200:
            raise  ValidationError("Error Code : %s - %s" % (response_data.status_code, response_data.reason))
        response_datas = response_data.json()
        _logger.info("Response Data: %s" % (response_datas))
        if isinstance(response_datas, dict):
            response_datas = [response_datas]
        for list in response_datas:
            id = list.get('list_id')
            self.klaviyo_id = id
        return {
            'effect': {
                'fadeout': 'slow',
                'message': "Yeah! Klaviyo list has been exported.",
                'img_url': '/web/static/src/img/smile.svg',
                'type': 'rainbow_man',
            }
        }

    def export_partner_from_odoo_to_klaviyo(self):
        credential_id = self.env['klaviyo.credential.details'].search([], limit=1)
        if not credential_id:
            raise ValidationError("Credentials not available!")
        for customer_id in self.klavio_customer_ids:
            if customer_id.exported_in_klaviyo:
                continue
            if not customer_id.partner_id and customer_id.partner_id.email:
                customer_id.message = "E-Mail Not Set!"
                continue
            request_data = {
                "api_key": credential_id.klaviyo_api_key,
                "profiles": [{
                    "email": "%s" % (customer_id.partner_id.email),
                }]
            }
            data = json.dumps(request_data)
            api_url = "%s/api/v2/list/%s/members" % (credential_id.klaviyo_api_url,self.klaviyo_id)
            _logger.info("Request Data: %s" % (data))
            headers = {'Content-Type': 'application/json'}
            try:
                response_data = request(method='POST', url=api_url, data=data, headers=headers)
            except Exception as e:
                customer_id.message = e
                continue
            if response_data.status_code != 200:
                customer_id.message = "Error Code : %s - %s" % (response_data.status_code, response_data.reason)
                continue
            response_datas = response_data.json()
            _logger.info("Response Data: %s" % (response_datas))
            if isinstance(response_datas, dict):
                response_datas = [response_datas]
            for list in response_datas:
                id = list.get('id')
                customer_id.message = "Exported In Klaviyo"
                customer_id.klaviyo_list_id = self.id
                customer_id.exported_in_klaviyo = True
                customer_id.klaviyo_list_id =self.id
                customer_id.klaviyo_referance= id
        return {
            'effect': {
                'fadeout': 'slow',
                'message': "Yeah! Klaviyo Customer has been exported.",
                'img_url': '/web/static/src/img/smile.svg',
                'type': 'rainbow_man',
            }
        }


class klaviyocustomerDetails(models.Model):
    _name = "klaviyo.customer.details"
    partner_id = fields.Many2one('res.partner', string="Partner")
    klaviyo_list_id = fields.Many2one('klaviyo.list.details', string="Klaviyo List")
    exported_in_klaviyo = fields.Boolean(copy=False, string="Exported In Klaviyo", default=False)
    klaviyo_referance = fields.Char(string = 'Klaviyo Customer Reference')
    message = fields.Char(string="Message")
