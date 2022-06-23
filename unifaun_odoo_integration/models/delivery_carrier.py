# -*- coding: utf-8 -*-
import json
import requests
from .unifaun import Unifaun
from odoo import fields, models
from odoo.exceptions import ValidationError


class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'

    delivery_type = fields.Selection(selection_add=[("unifaun", "Unifaun")],
                                     ondelete={'unifaun': 'set default'})
    unifaun_checkout_id = fields.Char(string='Delivery Checkout Id')
    label_size = fields.Selection([('laser-a5', ' Single A5 label'), ('laser-2a5', 'Two A5 labels on A4 paper'),
                                   ('laser-ste', 'Two STE labels (107x251 mm) on A4 paper'),
                                   ('laser-a4', 'Normal A4 used for waybills'),
                                   ('thermo-se', '107 x 251 mm thermo STE label'),
                                   ('thermo-190', '107 x 190 mm thermo label'),
                                   ('thermo-brev3', '107 x 72 mm thermo label'),
                                   ('thermo-165', '107 x 165 mm thermo label')], string='Label Size')
    carrier_partner_id = fields.Char(string='Partner ID', help='Partner id of you carrier')
    carrier_customer_number = fields.Char(string='Customer Number', help='Customer number of you carrier')
    carrier_service_id = fields.Char(string='Service ID', help='Carrier service id of your carrier')
    default_package_id = fields.Many2one('product.packaging', string='Default Package')

    def unifaun_rate_shipment(self, order):
        return {'success': True, 'price': 0.0, 'error_message': False, 'warning_message': False}

    def prepare_unifaun_shipment(self, picking):
        receiver_address = picking.unifaun_pickup_address_ids and picking.unifaun_pickup_address_ids
        sender_address = picking and picking.sale_id and picking.sale_id.warehouse_id and picking.sale_id.warehouse_id.partner_id

        prepare_id = picking.name.replace('/', '') + fields.datetime.now().strftime("%H%M%S")
        # prepare parcel
        parcel_data = []
        for package_id in picking.package_ids:
            parcel_data.append({
                "copies": "1",
                "weight": package_id.shipping_weight,
                "length": package_id.packaging_id.packaging_length or 0.0,
                "width": package_id.packaging_id.width or 0.0,
                "height": package_id.packaging_id.height or 0.0,
                "packageCode": package_id.packaging_id.unifaun_package_code or " "

            }, )
        if picking.weight_bulk:
            parcel_data.append({
                "copies": "1",
                "weight": picking.weight_bulk or 0.0,
                "length": self.default_package_id.packaging_length or 0.0,
                "width": self.default_package_id.width or 0.0,
                "height": self.default_package_id.height or 0.0,
                "packageCode": self.default_package_id.unifaun_package_code or " "

            })
        request_data = {
            "shipment": {
                "sender": {
                    "name": sender_address.name,
                    "address1": sender_address.street,
                    "zipcode": sender_address.zip,
                    "city": sender_address.city,
                    "country": sender_address and sender_address.country_id and sender_address.country_id.code,
                    "phone": sender_address.phone,
                    "email": sender_address.email
                },
                "senderPartners": [
                    {
                        "id": self.carrier_partner_id or ' ',
                        "custNo": self.carrier_customer_number or ' '
                    }
                ],
                "service": {
                    "id": self.carrier_service_id or ' '
                },
                "receiver": {
                    "name": receiver_address.agent_name or ' ',
                    "address1": receiver_address.agent_address1 or ' ',
                    "zipcode": receiver_address.agent_zipCode or ' ',
                    "city": receiver_address.agent_city or ' ',
                    "country": receiver_address.agent_country or ' ',
                    "phone": receiver_address.agent_phone or '',
                },
                "parcels": parcel_data,
                "orderNo": picking and picking.name,
            },
            "selectedOptionId": picking and picking.unifaun_pickup_address_ids.suboption_id,
            "prepareId": prepare_id,
            "returnShipmentData": "True",
            "language": "en"
        }
        return request_data

    def unifaun_send_shipping(self, pickings):
        # create prepare shipment
        shipment_data = self.prepare_unifaun_shipment(picking=pickings)
        response = Unifaun.send_request(prepare_id=False, data=json.dumps(shipment_data), carrier_id=self,
                                        methods='POST',
                                        params=False,
                                        service='prepare_shipment')
        prepare_id = response and response.get('prepareId')
        if prepare_id:
            # get label from prepare id
            shipment_data.pop('prepareId')
            shipment_data.update({'printConfig': {'target1Media': self.label_size, 'target1Type': 'pdf'}})
            response_data = Unifaun.send_request(prepare_id=prepare_id, data=json.dumps(shipment_data), carrier_id=self,
                                                 methods='POST', params=False, service='create_shipment')
            tracking_number = []
            for data in response_data:
                id = data.get('id')
                shipment_no = data.get('shipmentNo')
                tracking_number.append(shipment_no)
                prints = data.get('prints')
                for values in prints:
                    label_url = values.get('href')
                    label_id = values.get('id')
                    label_data = self.download_label_data(url=label_url)
                    message = ((
                                   "Label created!<br/> <b>Id : </b>%s<br/>") % (
                                   label_id,))
                    pickings.message_post(body=message, attachments=[
                        ('%s.%s' % (label_id, "pdf"), label_data)])
        else:
            pass
        shipping_data = {
            'exact_price': float(0.0),
            'tracking_number': ','.join(tracking_number)}
        shipping_data = [shipping_data]
        return shipping_data

    def download_label_data(self, url):
        combine_id = self.company_id and self.company_id.unifaun_combine_id
        headers = {
            "Authorization": "Bearer {}".format(combine_id)
        }
        response_data = requests.get(url=url, headers=headers)
        if response_data.status_code in [200, 201]:
            return response_data.content
        else:
            return False

    def unifaun_cancel_shipment(self, pickings):
        raise ValidationError('For Cancel Service Please Contact To Vraja Technologies')

    def unifaun_get_tracking_link(self, picking):
        raise ValidationError('For Tracking Service Please Contact To Vraja Technologies')