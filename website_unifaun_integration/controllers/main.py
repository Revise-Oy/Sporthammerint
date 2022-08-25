from odoo import fields, http, tools, _
from odoo.http import request
from odoo.addons.unifaun_shipping_integration.models.sale_order import SaleOrder
import requests
import logging

_logger = logging.getLogger(__name__)


# from odoo.addons.ups_shipping_odoo_integration.models.ups_response import Response


class WebsiteSale(http.Controller):

    @http.route(['/unifaun_service'], type='json', auth='public', methods=['POST'], website=True,
                csrf=False)
    def unifaun_service(self, **post):
        results = {}
        if post.get('order') and post.get('delivery_type'):
            delivery_method = request.env['delivery.carrier'].sudo().browse(int(post.get('delivery_type')))
            if delivery_method.delivery_type == 'unifaun' and delivery_method.create_shipment_pl_flag:
                results = request.env['ir.ui.view']._render_template(
                    'website_unifaun_integration.unifaun_shipping_location')
            order = request.website.sale_get_order()
            if order and order.carrier_id and not order.carrier_id.create_shipment_pl_flag:
                existing_records = request.env['unifaun.pickup.address'].sudo().search([('sale_id', '=', order.id)])
                existing_records.sudo().unlink()
            if order.order_line.filtered(lambda x: x.product_id.categ_id.is_bicycle_category) and post.get('bicycle_category'):
                return request.env['delivery.carrier'].search([('is_bicycle_category', '=', True)]).ids
        return results

    @http.route(['/get_location'], type='json', auth='public', methods=['POST'], website=True, csrf=False)
    def get_location(self, **post):
        order = request.website.sale_get_order()
        try:
            if True:
                order.get_uni_pickup_location()
                values = {
                    'locations': order.unifaun_location_ids or []
                }
                tamplate = request.env['ir.ui.view']._render_template(
                    'website_unifaun_integration.unifaun_location_details', values)
                # return {'template': tamplate, 'dic': dic}
                return {'template': tamplate}
            else:
                return {'error': "Location Not Found For This Address!"}

        except Exception as e:
            return False

    @http.route(['/set_location'], type='json', auth='public', website=True, csrf=False)
    def set_location(self, location=False, **post):
        location_id = request.env['unifaun.pickup.address'].sudo().browse(location)
        if location_id and location_id.id:
            location_id.sale_id.unifaun_location_id = location_id.id
            return {'success': True, 'location_name': location_id.agent_name, 'street': location_id.agent_address1,
                    'city': location_id.agent_city, 'zip': location_id.agent_zipCode,
                    'street2': location_id.agent_address2}
