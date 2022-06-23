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
    create_shipment_pl_flag = fields.Boolean(string='Create Shipment Using Pickup Location')
    label_size = fields.Selection([('laser-a5', ' Single A5 label'), ('laser-2a5', 'Two A5 labels on A4 paper'),
                                   ('laser-ste', 'Two STE labels (107x251 mm) on A4 paper'),
                                   ('laser-a4', 'Normal A4 used for waybills'),
                                   ('thermo-se', '107 x 251 mm thermo STE label'),
                                   ('thermo-190', '107 x 190 mm thermo label'),
                                   ('thermo-brev3', '107 x 72 mm thermo label'),
                                   ('thermo-165', '107 x 165 mm thermo label')], string='Label Size')
    carrier_partner_id = fields.Char(string='Partner ID', help='Partner id of you carrier')
    carrier_customer_number = fields.Char(string='Customer Number', help='Customer number of you carrier')
    carrier_delivery_option_id = fields.Char(string='Delivery Option Id', help='Delivery Option Id of your carrier')
    carrier_service_id = fields.Char(string='Service ID', help='Carrier service id of your carrier')
    default_package_id = fields.Many2one('stock.package.type', string='Default Package')

    def unifaun_rate_shipment(self, order):
        return {'success': True, 'price': 0.0, 'error_message': False, 'warning_message': False}

    def package_volume(self, picking):
        parcel_data = []
        for package_id in picking.package_ids:
            parcel_data.append(
                package_id.package_type_id.packaging_length * package_id.package_type_id.width * package_id.package_type_id.height)
            return sum(parcel_data)
        if picking.weight_bulk:
            return self.default_package_id.packaging_length * self.default_package_id.width * self.default_package_id.height

    def prepare_unifaun_shipment(self, picking):
        # if self.create_shipment_pl_flag:
        #     receiver_address = picking.unifaun_pickup_address_id and picking.unifaun_pickup_address_id
        #     rec_name = "{}".format(receiver_address.agent_name or ' ')
        #     rec_address1 = "{}".format(receiver_address.agent_address1 or ' ')
        #     rec_zipcode = "{}".format(receiver_address.agent_zipCode or ' ')
        #     rec_city = "{}".format(receiver_address.agent_city or ' ')
        #     rec_country = "{}".format(receiver_address.agent_country or ' ')
        #     rec_phone = "{}".format(
        #         receiver_address.agent_phone or picking and picking.partner_id and picking.partner_id.mobile or picking.partner_id.phone or '')
        #     rec_email = "{}".format(receiver_address.agent_email or picking.partner_id.email or '')
        # else:
        receiver_address = picking.partner_id
        rec_name = "{}".format(receiver_address.name or ' ')
        rec_address1 = "{}".format(picking.partner_id and picking.partner_id.street)
        rec_zipcode = "{}".format(receiver_address.zip or ' ')
        rec_city = "{}".format(receiver_address.city or ' ')
        rec_country = "{}".format(receiver_address.country_id and receiver_address.country_id.code or ' ')
        rec_phone = "{}".format(receiver_address.phone or receiver_address.mobile or ' ')
        rec_email = "{}".format(receiver_address.email)

        if not rec_email or not rec_phone:
            raise ValidationError("Receiver phone number and email are missing")
        sender_address = picking and picking.sale_id and picking.sale_id.warehouse_id and picking.sale_id.warehouse_id.partner_id
        # prepare parcel
        parcel_data = []
        for package_id in picking.package_ids:
            parcel_data.append({
                "copies": "1",
                "weight": package_id.shipping_weight,
                "length": package_id.package_type_id.packaging_length or 0.0,
                "width": package_id.package_type_id.width or 0.0,
                "height": package_id.package_type_id.height or 0.0,
                "packageCode": package_id.package_type_id.unifaun_package_code or " "

            }, )
        if picking.weight_bulk:
            parcel_data.append({
                "copies": "1",
                "weight": picking.shipping_weight or 0.0,
                "length": self.default_package_id.packaging_length or 0.0,
                "width": self.default_package_id.width or 0.0,
                "height": self.default_package_id.height or 0.0,
                "packageCode": self.default_package_id.unifaun_package_code or " "

            })
        request_data = {
            "shipment": {
                "sender": {
                    "name": sender_address.name or " ",
                    "address1": sender_address.street or " ",
                    "zipcode": sender_address.zip or " ",
                    "city": sender_address.city or " ",
                    "country": sender_address and sender_address.country_id and sender_address.country_id.code or " ",
                    "phone": sender_address.phone or sender_address.mobile or " ",
                    "email": sender_address.email or " "
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
                    "name": rec_name,
                    "address1": rec_address1,
                    "zipcode": rec_zipcode,
                    "city": rec_city,
                    "country": rec_country,
                    "mobile": rec_phone,
                    "email": rec_email
                },
                "parcels": parcel_data,
                "totalvolume": "{}".format(self.package_volume(picking=picking)),
                "orderNo": picking and picking.name or " ",
            },
            # "selectedOptionId": picking and picking.unifaun_pickup_address_ids.suboption_id,
            # "prepareId": prepare_id,
            # "returnShipmentData": "True",
            # "language": "en"
        }
        return request_data

    def unifaun_send_shipping(self, pickings):
        # create prepare shipment
        if not self.create_shipment_pl_flag:

            shipment_data = self.prepare_unifaun_shipment(pickings)
            shipment_data.update({'printConfig': {'target1Media': self.label_size, 'target1Type': 'pdf'}})

            response = Unifaun.send_request(prepare_id=False, data=json.dumps(shipment_data), carrier_id=self,
                                            methods='POST',
                                            params=False,
                                            service='shipment')
            tracking_number = self.attach_label_message_post(response_data=response, pickings=pickings)
        else:
            # prepare request data
            shipment_data = self.prepare_unifaun_shipment(picking=pickings)
            # add agent information in request data (Add agent details in only pickup location service)
            agent = pickings and pickings.unifaun_pickup_address_id
            if agent:
                shipment_data.get('shipment').update({'agent': {
                    "name": agent.agent_name,
                    "address1": agent.agent_address1,
                    "zipcode": agent.agent_zipCode,
                    "city": agent.agent_city,
                    "country": agent.agent_country
                }})
            prepare_id = pickings.name.replace('/', '') + fields.datetime.now().strftime("%H%M%S")

            shipment_data.update({'selectedOptionId': pickings and pickings.unifaun_pickup_address_id.suboption_id})
            shipment_data.update({'prepareId': prepare_id})
            shipment_data.update({'returnShipmentData': "True"})
            shipment_data.update({'language': "en"})

            response = Unifaun.send_request(prepare_id=False, data=json.dumps(shipment_data), carrier_id=self,
                                            methods='POST',
                                            params=False,
                                            service='prepare_shipment')
            prepare_id = response and response.get('prepareId')
            if prepare_id:
                # get label from prepare id
                if self.create_shipment_pl_flag:
                    agent = pickings and pickings.unifaun_pickup_address_id
                    if agent:
                        shipment_data.get('shipment').update({'agent': {
                            "name": agent.agent_name,
                            "address1": agent.agent_address1,
                            "zipcode": agent.agent_zipCode,
                            "city": agent.agent_city,
                            "country": agent.agent_country
                        }})
                shipment_data.pop('prepareId')
                shipment_data.update({'printConfig': {'target1Media': self.label_size, 'target1Type': 'pdf'}})
                response_data = Unifaun.send_request(prepare_id=prepare_id, data=json.dumps(shipment_data),
                                                     carrier_id=self,
                                                     methods='POST', params=False, service='create_shipment')

                tracking_number = self.attach_label_message_post(response_data=response_data, pickings=pickings)
            else:
                raise ValidationError("Prepare ID not found in response \n {}".format(response))
        shipping_data = {
            'exact_price': float(0.0),
            'tracking_number': ','.join(tracking_number)}
        shipping_data = [shipping_data]
        return shipping_data

    def attach_label_message_post(self, response_data, pickings):
        tracking_number = []
        for data in response_data:
            id = data.get('id')
            shipment_no = data.get('shipmentNo')
            if shipment_no:
                tracking_number.append(shipment_no)
            else:
                tracking_number.append(id)
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
        return tracking_number

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
