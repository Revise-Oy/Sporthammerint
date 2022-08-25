from odoo import fields, models

class StockMove(models.Model):
    _inherit = 'stock.move'

    def _get_new_picking_values(self):
        res = super(StockMove, self)._get_new_picking_values()
        location_id = self.sale_line_id and self.sale_line_id and self.sale_line_id.order_id and self.sale_line_id.order_id.unifaun_location_id
        if location_id:
            res.update({'unifaun_pickup_address_id': location_id.id})
        return res