odoo.define('pos_all_in_one.ReceiptScreen', function(require) {
	"use strict";

	const Registries = require('point_of_sale.Registries');
	const ReceiptScreen = require('point_of_sale.ReceiptScreen');

	const BiReceiptScreen = (ReceiptScreen) =>
		class extends ReceiptScreen {
			constructor() {
				super(...arguments);
			}

			update_prod_qty(){
				let self = this;
				const order = this.currentOrder;
				let config = this.env.pos.config;
				let stock_update = self.env.pos.company.point_of_sale_update_stock_quantities;
				if (order.is_paying_partial == false && config.pos_display_stock === true && stock_update == 'real' && 
					(config.pos_stock_type == 'onhand' || config.pos_stock_type == 'available')){
					order.get_orderlines().forEach(function (line) {
						var product = line.product;
						product['bi_on_hand'] -= line.get_quantity();
						product['bi_available'] -= line.get_quantity();
						product.qty_available -= line.get_quantity();
						self.load_product_qty(product);
					}) 
				}
				self.env.pos.set("is_sync",true);
			}

		};

	Registries.Component.extend(ReceiptScreen, BiReceiptScreen);
	return ReceiptScreen;

});
