// BiProductScreen js
odoo.define('pos_orders_all.productScreen', function(require) {
	"use strict";

	const Registries = require('point_of_sale.Registries');
	const ProductScreen = require('point_of_sale.ProductScreen'); 

	const BiProductScreen = (ProductScreen) =>
		class extends ProductScreen {
			constructor() {
				super(...arguments);
			}
			
			async _clickProduct(event) {
				let self = this;
				const product = event.detail;
				let allow_order = self.env.pos.config.pos_allow_order;
				let pos_config = self.env.pos.config;
				let deny_order= self.env.pos.config.pos_deny_order;
				let call_super = true;
				if(self.env.pos.config.pos_display_stock){
					if(self.env.pos.config.show_stock_location == 'specific' && product.type == 'product'){
						var partner_id = self.env.pos.get_client();
						var location = self.env.pos.locations;
						await this.rpc({
							model: 'stock.quant',
							method: 'get_single_product',
							args: [partner_id ? partner_id.id : 0,product.id, location],
						}).then(function(output) {
							if (pos_config.pos_stock_type == 'onhand'){
								if (allow_order == false){
									if ( (product.qty_available <= deny_order) || (product.qty_available <= 0) ){
										call_super = false;
										self.showPopup('ErrorPopup', {
											title: self.env._t('Deny Order'),
											body: self.env._t("Deny Order" + "(" + product.display_name + ")" + " is Out of Stock."),
										});
									}
								}
								else if(allow_order == true){
									if (product.qty_available <= deny_order){
										call_super = false;
										self.showPopup('ErrorPopup', {
											title: self.env._t('Deny Order'),
											body: self.env._t("Deny Order" + "(" + product.display_name + ")" + " is Out of Stock."),
										});
									}
								}
							}
							if (pos_config.pos_stock_type == 'incoming'){
								if (allow_order == false){
									if ( (product.incoming_qty <= deny_order) || (product.incoming_qty <= 0) ){
										call_super = false;
										self.showPopup('ErrorPopup', {
											title: self.env._t('Deny Order'),
											body: self.env._t("Deny Order" + "(" + product.display_name + ")" + " is Out of Stock."),
										});
									}
								}
								else if(allow_order == true){
									if (product.incoming_qty <= deny_order){
										call_super = false;
										self.showPopup('ErrorPopup', {
											title: self.env._t('Deny Order'),
											body: self.env._t("Deny Order" + "(" + product.display_name + ")" + " is Out of Stock."),
										});
									}
								}
							}
							if (pos_config.pos_stock_type == 'outgoing'){
								if (allow_order == false){
									if ( (product.outgoing_qty <= deny_order) || (product.outgoing_qty <= 0) ){
										call_super = false;
										self.showPopup('ErrorPopup', {
											title: self.env._t('Deny Order'),
											body: self.env._t("Deny Order" + "(" + product.display_name + ")" + " is Out of Stock."),
										});
									}
								}
								else if(allow_order == true){
									if (product.outgoing_qty <= deny_order){
										call_super = false;
										self.showPopup('ErrorPopup', {
											title: self.env._t('Deny Order'),
											body: self.env._t("Deny Order" + "(" + product.display_name + ")" + " is Out of Stock."),
										});
									}
								}
							}
							if (pos_config.pos_stock_type == 'available'){
								if (allow_order == false){
									if ( (product.virtual_available <= deny_order) || (product.virtual_available <= 0) ){
										call_super = false;
										self.showPopup('ErrorPopup', {
											title: self.env._t('Deny Order'),
											body: self.env._t("Deny Order" + "(" + product.display_name + ")" + " is Out of Stock."),
										});
									}
								}
								else if(allow_order == true){
									if (product.virtual_available <= deny_order){
										call_super = false;
										self.showPopup('ErrorPopup', {
											title: self.env._t('Deny Order'),
											body: self.env._t("Deny Order" + "(" + product.display_name + ")" + " is Out of Stock."),
										});
									}
								}
							}
							
						});
					}
					else{
						if (product.type == 'product' && allow_order == false){
							if (product.qty_available <= deny_order && allow_order == false){
								call_super = false; 
								self.showPopup('ErrorPopup', {
									title: self.env._t('Deny Order'),
									body: self.env._t("Deny Order" + "(" + product.display_name + ")" + " is Out of Stock."),
								});
							}
							else if (product.qty_available <= 0 && allow_order == false){
								call_super = false; 
								self.showPopup('ErrorPopup', {
									title: self.env._t('Error: Out of Stock'),
									body: self.env._t("(" + product.display_name + ")" + " is Out of Stock."),
								});
							}
						}
						else if(product.type == 'product' && allow_order == true && product.qty_available <= deny_order){
							call_super = false; 
							self.showPopup('ErrorPopup', {
								title: self.env._t('Error: Out of Stock'),
								body: self.env._t("(" + product.display_name + ")" + " is Out of Stock."),
							});
						}
					}
				}
				if(call_super){
					super._clickProduct(event);
				}
			}

			async _onClickPay() {
				var self = this;
				let order = this.env.pos.get_order();
				let lines = order.get_orderlines();
				let pos_config = self.env.pos.config; 
				let allow_order = pos_config.pos_allow_order;
				let deny_order= pos_config.pos_deny_order;
				let call_super = true;
				if(pos_config.pos_display_stock){
					if (pos_config.show_stock_location == 'specific'){
						let partner_id = self.env.pos.get_client();
						let location = self.env.pos.locations;
						let prods = [];

						$.each(lines, function( i, line ){
							if (line.product.type == 'product'){
								prods.push(line.product.id)
							}
						});
						await this.rpc({
							model: 'stock.quant',
							method: 'get_products_stock_location_qty',
							args: [partner_id ? partner_id.id : 0, location,prods,pos_config.pos_stock_type],
						}).then(function(output) {
							var flag = 0;
							var out_of_stock_prod = []
							for (var i = 0; i < lines.length; i++) {
								for (var j = 0; j < output.length; j++) {
									var values = $.map(output[0], function(value, key) { 
										var keys = $.map(output[0], function(value, key) {
											if (lines[i].product.type == 'product' && lines[i].product['id'] == key ){
												var product = self.env.pos.db.get_product_by_id(lines[i].product.id)
												if (allow_order == false && lines[i].quantity > value){
													flag = flag + 1;
													if (out_of_stock_prod.includes(lines[i].product)){
													}
													else{
														out_of_stock_prod.push(lines[i].product)
													}	
												}
												var check = value - lines[i].quantity;
												if (allow_order == true && deny_order > check){
													flag = flag + 1;
													out_of_stock_prod.push(lines[i].product)
												}
											}
										});
									});
								}
							}
							if(flag > 0){
								call_super = false;
								var msg = " ";
								for (i in out_of_stock_prod){
									msg += out_of_stock_prod[i].name+"\n\n "
								}
								self.showPopup('outOfStock', {
									title: self.env._t('Out Of Stock'),
									body: self.env._t(msg),
								});
							}
						});
					} else {
						var out_of_stock_prod_all = [];
						var msg = " ";

						for(var i = 0; i < lines.length; i++) {
							var line = lines[i];
							if (line.product.type == 'product'){
								if (allow_order == false && line.quantity > line.product['bi_on_hand']){
									call_super = false;
									if (!out_of_stock_prod_all.includes(line.product)){
										out_of_stock_prod_all.push(line.product)
									} 
								}
								var check = line.product['bi_on_hand'] - line.quantity;
								if(allow_order == true && check < deny_order){
									call_super = false; 
									if (!out_of_stock_prod_all.includes(line.product)){
										out_of_stock_prod_all.push(line.product)
									}
								}
							}
						}
						
						if(! call_super){
							var msg = '' 
							for (var i in out_of_stock_prod_all){
								msg = msg + out_of_stock_prod_all[i].name+"\n\n "
							}
							self.showPopup('outOfStock', {
								title: self.env._t('Denied Order'),
								body: self.env._t(msg),
							});
							return
						}
					}
				}
				if(call_super){
					super._onClickPay();
				}
			}
		};

	Registries.Component.extend(ProductScreen, BiProductScreen);

	return ProductScreen;

});
