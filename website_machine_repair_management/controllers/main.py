# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import http, SUPERUSER_ID, _
from odoo.http import request
from datetime import datetime, date

class WebsiteMachineRepair(http.Controller):

	@http.route(['/machine'], type='http', auth="public", website=True)
	def machine_repair(self, **post):
		
		return request.render("website_machine_repair_management.machine_repair")
	
	@http.route(['/machine/thankyou'], type='http', auth="public", website=True)
	def machine_thankyou(self, **post):
		
		machine_obj = request.env['machine.repair']
		machine_line_obj = request.env['machine.repair.line']
		
		#delivery = datetime.strptime(post['delivery_date'], DEFAULT_SERVER_DATE_FORMAT).strftime(DEFAULT_SERVER_DATE_FORMAT)
		
		subject = post.get('name',False)
		contact_name = post.get('contact_name',False)
		street = post.get('street',False)
		email = post.get('email',False)
		city =  post.get('city',False)
		contact_mobile = post.get('contact_mobile',False)
		serial = post.get('serial',False)
		machine_name = post.get('machine_name',False)
		partner_id = post.get('client_id',False)
		product_id = post.get('product_id',False)
		phone = post.get('phone',False)
		under_guarantee = post.get('under_guarantee',False)
		type_guarantee = post.get('type',False)
		
		machine_obj = request.env['machine.repair']
		machine_line_obj = request.env['machine.repair.line']
		
		if subject:
			gr_y = []
			gr_pay = []
			if under_guarantee == 'yes':
				gr_y = 'yes'
			else:
				gr_y = 'no'
				
			if type_guarantee == 'free':
				gr_pay = 'free'
			else:
				gr_pay = 'paid'
			
			client_obj = request.env['res.partner'].sudo().search([('name','=', partner_id)])
			if not client_obj:
				client_obj.sudo().create({
					'name': partner_id,
					'street': street,
					'city': city,
					'phone': phone,
					'mobile': contact_mobile,
					'email': email,
				})
				
			client = []
			machine_client_obj = request.env['res.partner'].sudo().search([('name','=', partner_id)])
			for i in machine_client_obj:
				client = i.id

			if not product_id:
				return request.redirect("/machine?product_msg=1")

			serial_lot_w = request.env['stock.production.lot'].search([('product_id','=', int(product_id)),('name','=', serial)])


			serial_no_valid = []
			if serial_lot_w:
				serial_no_valid = serial_lot_w.id
			else:
				return request.redirect("/machine?repair_msg=1")
				# return request.redirect("/machine?repair_msg=%s" % _("Invalid Serial No !"))
			
			user = request.env['res.users']._context.get('uid', False)
			if user != False:
				user_id = request.env['res.users'].browse(request.env['res.users']._context['uid'])
			else:
				user_id = request.env['res.users'].sudo().browse(SUPERUSER_ID)
			
			machine_id = machine_obj.sudo().create({
							'name': subject,
							'user_id':user_id.id,
							'client_phone': phone,
							'client_mobile': contact_mobile,
							'client_email': email,
							'contact_name': contact_name,
							'receipt_date': datetime.now(),
							'client_id': client,
					})
			machine_line_obj.sudo().create({
				'machine_id': product_id,
				'serial_no': serial_no_valid,
				'machine_repair_id': machine_id.id,
				'guarantee': gr_y,
				'guarantee_type': gr_pay,
				'machine_name': machine_name,
			
			})
			
			return request.render("website_machine_repair_management.machine_thankyou")
		
		else:	
			return request.redirect("/machine?detail_msg=1")		
				   
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:        
