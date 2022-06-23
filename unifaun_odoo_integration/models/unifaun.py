import requests
import logging
from odoo import _
from odoo.exceptions import ValidationError

_logger = logging.getLogger('Unifaun')


def _parse_error_msg(response_data):
    bad_character = ["(", ")", "-", "+", "\\", "{", "}", "[", "]", ":"]
    message = ''.join((filter(lambda i: i not in bad_character, response_data.text)))
    message = message.replace('"errors"', "")
    return "Status Code : %s %s" % (response_data.status_code, message)


def _prepare_api_url(carrier_id, prepare_id, service):
    checkout_id = carrier_id and carrier_id.unifaun_checkout_id
    host_name = carrier_id and carrier_id.company_id and carrier_id.company_id.unifaun_api_url
    if not host_name:
        raise ValidationError(_("Please define host name in {} company").format(carrier_id and carrier_id.company_id
                                                                                and carrier_id.company_id.name))
    if not checkout_id:
        raise ValidationError(_("Please define delivery checkout id in {}".format(carrier_id.name)))
    if service == 'get_checkout':
        return '%s/rs-extapi/v1/delivery-checkouts/%s' % (host_name, checkout_id)
    if service == 'prepare_shipment':
        return '%s/rs-extapi/v1/delivery-checkouts/%s' % (host_name, checkout_id)
    if service == 'create_shipment':
        return '%s/rs-extapi/v1/prepared-shipments/%s/shipments' %(host_name, prepare_id)


class Unifaun():
    def send_request(prepare_id, data, carrier_id, methods, params, service):
        api_url = _prepare_api_url(carrier_id=carrier_id,prepare_id=prepare_id, service=service)
        combine_id = carrier_id and carrier_id.company_id and carrier_id.company_id.unifaun_combine_id
        if not combine_id:
            raise ValidationError(_("Please define combine id in company"))
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(combine_id)
        }

        try:
            _logger.info(":::: send {0} to {1}".format(methods, api_url))
            _logger.info(":::: request data {}".format(data))
            response_data = requests.request(method=methods, url=api_url, data=data, params=params, headers=headers)
            if response_data.status_code in [200, 201]:
                _logger.info(":::::: successfully response from {}".format(api_url))
                _logger.info(":::: response data {}".format(response_data.text))
                response_data = response_data.json()
                return response_data
            else:
                msg = _parse_error_msg(response_data=response_data)
                raise ValidationError(_(msg))
        except Exception as error:
            raise ValidationError(_(error))
