import base64
from requests import request
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError, Warning


class klaviyoCredentailDetails(models.Model):
    _name = "klaviyo.credential.details"

    name = fields.Char("Name", required=True, help="klaviyo Credential Configuration")
    klaviyo_api_key = fields.Char("klaviyo API KEY", required=True, help="klaviyo Consumer Secret")
    klaviyo_api_url = fields.Char(string='klaviyo API URL', default="https://a.klaviyo.com")

    def create_klaviyo_operation_detail(self, operation, operation_type, req_data, response_data, operation_id,
                                            company_id=False, fault_operation=False, process_message=False):
        klaviyo_operation_details_obj = self.env['klaviyo.operation.details']
        vals = {
            'klaviyo_operation': operation,
            'klaviyo_operation_type': operation_type,
            'klaviyo_request_message': '{}'.format(req_data),
            'klaviyo_response_message': '{}'.format(response_data),
            'operation_id': operation_id.id,
            'company_id': company_id and company_id.id or False,
            'fault_operation': fault_operation,
            'process_message': process_message,
        }
        operation_detail_id = klaviyo_operation_details_obj.create(vals)
        return operation_detail_id

    def import_lists_from_klavio(self):
        klaviyo_list_details_obj = self.env['klaviyo.list.details']
        klaviyo_list_details_obj.klaviyo_to_odoo_import_lists(self)
        return {
            'effect': {
                'fadeout': 'slow',
                'message': "Yeah! Klaviyo Lists has been retrieved.",
                'img_url': '/web/static/src/img/smile.svg',
                'type': 'rainbow_man',
            }
        }

    def create_klaviyo_operation(self, operation, operation_type, log_message, company_id):
        klaviyo_operation_obj = self.env['klaviyo.operation']
        vals = {
            'klaviyo_operation': operation,
            'klaviyo_operation_type': operation_type,
            'company_id': company_id and company_id.id or False,
            'klaviyo_credential_id':self.id ,
            'klaviyo_message': log_message
        }
        operation_id = klaviyo_operation_obj.create(vals)
        return operation_id

    def api_calling_function(self, url):
        try:
            response_data = request(method='GET', url=url)
            return response_data
        except Exception as e:
            raise ValidationError(e)

    def making_klaviyo_url(self, api_name):
        if self.klaviyo_api_url:
            url = self.klaviyo_api_url + api_name
            return url
        else:
            raise ValidationError(_("URL is not appropriate."))
