# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _
from datetime import date, time, datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo import tools
from odoo.exceptions import UserError
from odoo.exceptions import Warning


class machine_repair(models.Model):
	_name = 'machine.repair'
	_inherit = ['mail.thread']
	_order = 'id desc'

	name = fields.Char(string='Subject', required=True)
	sequence = fields.Char(string='Sequence', readonly=True, copy=False, default="New")
	client_id = fields.Many2one('res.partner', string='Client', required=True)
	client_phone = fields.Char(string='Phone')
	client_mobile = fields.Char(string='Mobile')
	client_email = fields.Char(string='Email')
	receipt_date = fields.Date(string='Date of Receipt', default=date.today().strftime(DEFAULT_SERVER_DATE_FORMAT))
	contact_name = fields.Char(string='Contact Name')
	phone = fields.Char(string='Contact Number')
	model_number = fields.Char(string='Model #')
	machine_id = fields.Many2one('product.product', string='Machine')
	machine_name = fields.Char(string='Machine Name')
	serial_no = fields.Many2one('stock.production.lot', string='Serial Number')
	guarantee = fields.Selection(
		[('yes', 'Yes'), ('no', 'No')], string='Under Guarantee?')
	guarantee_type = fields.Selection(
		[('paid', 'paid'), ('free', 'Free')], string='Guarantee Type')
	service_type = fields.Many2one('service.type', string='Nature of Service')
	user_id = fields.Many2one('res.users', string='Assigned to', default=lambda self: self._uid)
	priority = fields.Selection([('0','Low'), ('1','Normal'), ('2','High')], 'Priority')
	description = fields.Text(string='Notes')
	service_detail = fields.Text(string='Service Details')
	state = fields.Selection([
		('draft', 'Received'),
		('diagnosis', 'In Diagnosis'),
		('diagnosis_complete', 'Diagnosis Complete'),
		('quote', 'Quotation Sent'),
		('saleorder', 'Quotation Approved'),
		('workorder', 'Work in Progress'),
		('work_completed', 'Work Completed'),
		('invoiced', 'Invoiced'),
		('done', 'Done'),
		('cancel', 'Cancelled'),
		], 'Status', readonly=True, copy=False, help="Gives the status of the machine repairing.", index=True, default='draft')
	diagnose_id = fields.Many2one('machine.diagnose', string='Machine Diagnose')
	workorder_id = fields.Many2one('machine.workorder', string='Machine Work Order')
	sale_order_id = fields.Many2one('sale.order', string='Sales Order', copy=False)
	confirm_sale_order = fields.Boolean('is confirm')
	machine_repair_line = fields.One2many('machine.repair.line', 'machine_repair_id', string="Machine Lines")
	workorder_count = fields.Integer(string='Work Orders', compute='_compute_workorder_id')
	dig_count  = fields.Integer(string='Diagnosis Orders', compute='_compute_dignosis_id')
	quotation_count = fields.Integer(string ="Quotations", compute='_compute_quotation_id')
	saleorder_count = fields.Integer(string = "Sale Order", compute='_compute_saleorder_id')
	inv_count = fields.Integer(string = "Invoice")

	@api.model
	def create(self, vals):
		vals['sequence'] = self.env['ir.sequence'].next_by_code('machine.repair') or 'New'       
		result = super(machine_repair, self).create(vals)       
		return result

	def button_view_diagnosis(self):
		list = []
		context = dict(self._context or {})
		dig_order_ids = self.env['machine.diagnose'].search([('machine_repair_id', '=', self.id)])           
		for order in dig_order_ids:
			list.append(order.id)
		return {
			'name': _('Machine Diagnosis'),
			'view_type': 'form',
			'view_mode': 'tree,form',
			'res_model': 'machine.diagnose',
			'view_id': False,
			'type': 'ir.actions.act_window',
			'domain': [('id', 'in',list )],
			'context': context,
		}

	
	def button_view_workorder(self):
		list = []
		context = dict(self._context or {})
		work_order_ids = self.env['machine.workorder'].search([('machine_repair_id', '=', self.id)])           
		for order in work_order_ids:
			list.append(order.id)
		return {
			'name': _('Machine Work Order'),
			'view_type': 'form',
			'view_mode': 'tree,form',
			'res_model': 'machine.workorder',
			'view_id': False,
			'type': 'ir.actions.act_window',
			'domain': [('id', 'in',list )],
			'context': context,
		}
  
	
	def button_view_quotation(self):
		list = []
		context = dict(self._context or {})
		quo_order_ids = self.env['sale.order'].search([('state', '=', 'draft'),('machine_repair_id', '=', self.id)])           
		for order in quo_order_ids:
			list.append(order.id)
		return {
			'name': _('Sale'),
			'view_type': 'form',
			'view_mode': 'tree,form',
			'res_model': 'sale.order',
			'view_id': False,
			'type': 'ir.actions.act_window',
			'domain': [('id', 'in',list )],
			'context': context,
		}
  
	
	def button_view_saleorder(self):
		list = []
		context = dict(self._context or {})
		quo_order_ids = self.env['sale.order'].search([('state', '=', 'sale'),('machine_repair_id', '=', self.id)])           
		for order in quo_order_ids:
			list.append(order.id)
		return {
			'name': _('Sale'),
			'view_type': 'form',
			'view_mode': 'tree,form',
			'res_model': 'sale.order',
			'view_id': False,
			'type': 'ir.actions.act_window',
			'domain': [('id', 'in',list )],
			'context': context,
		}
 
	
	def button_view_invoice(self):
		list = []
		inv_list  = []
		so_order_ids = self.env['sale.order'].search([('state', '=', 'sale'),('machine_repair_id', '=', self.id)])
		for order in so_order_ids:
			inv_order_ids = self.env['account.move'].search([('origin', '=',order.name )])            
			if inv_order_ids:
				for order_id in inv_order_ids:
					if order_id.id not in list:
						list.append(order_id.id)
							
		context = dict(self._context or {})
		return {
			'name': _('Invoice '),
			'view_type': 'form',
			'view_mode': 'tree,form',
			'res_model': 'account.move',
			'view_id': False,
			'type': 'ir.actions.act_window',
			'domain': [('id', 'in',list )],
			'context': context,
		}
	
	
	@api.depends('workorder_id')
	def _compute_workorder_id(self):
		for order in self:
			work_order_ids = self.env['machine.workorder'].search([('machine_repair_id', '=', order.id)])            
			order.workorder_count = len(work_order_ids)

	
	@api.depends('diagnose_id')
	def _compute_dignosis_id(self):
		for order in self:
			dig_order_ids = self.env['machine.diagnose'].search([('machine_repair_id', '=', order.id)])            
			order.dig_count = len(dig_order_ids)

	
	@api.depends('sale_order_id')
	def _compute_quotation_id(self):
		for order in self:
			quo_order_ids = self.env['sale.order'].search([('state', '=', 'draft'),('machine_repair_id', '=', order.id)])            
			order.quotation_count = len(quo_order_ids)
	
	
	@api.depends('confirm_sale_order')
	def _compute_saleorder_id(self):
		for order in self:
			order.quotation_count = 0
			so_order_ids = self.env['sale.order'].search([('state', '=', 'sale'),('machine_repair_id', '=', order.id)])            
			order.saleorder_count = len(so_order_ids)

	
	@api.depends('state')
	def _compute_invoice_id(self):
		count  = 0 
		if self.state== 'invoiced': 
			for order in self:
				so_order_ids = self.env['sale.order'].search([('state', '=', 'sale'),('machine_repair_id', '=', order.id)])
				for order in so_order_ids:
					inv_order_ids = self.env['account.move'].search([('origin', '=',order.name )])            
					if inv_order_ids:
						self.inv_count = len(inv_order_ids)
			
	
	def diagnosis_created(self):
		self.write({'state':'diagnosis'})

	
	def quote_created(self):
		self.write({'state':'quote'})

	
	def order_confirm(self):
		self.write({'state':'saleorder'})

	
	def machine_confirmed(self):
		self.write({'state':'confirm'})

	
	def workorder_created(self):
		self.write({'state':'workorder'})

	@api.onchange('client_id')
	def onchange_partner_id(self):
		addr = {}
		part = self.client_id
		if part:
			part.address_get(['contact'])
			addr['client_phone'] = part.phone
			addr['client_mobile'] = part.mobile
			addr['client_email'] = part.email
		return {'value': addr}

	
	def action_create_machine_diagnosis(self):
		Diagnosis_obj = self.env['machine.diagnose']
		Machine_line_obj = self.env['machine.repair.line']
		repair_obj = self.env['machine.repair'].browse(self.ids[0])
		mod_obj = self.env['ir.model.data']
		act_obj = self.env['ir.actions.act_window']
		if not repair_obj.machine_repair_line:
			raise Warning('You cannot create Machine Diagnosis without Machine.')
		
		diagnose_vals = {
			'service_rec_no': repair_obj.sequence,
			'name': repair_obj.name,
			'priority': repair_obj.priority,
			'receipt_date': repair_obj.receipt_date,
			'client_id': repair_obj.client_id.id,
			'contact_name': repair_obj.contact_name,
			'phone': repair_obj.phone,
			'client_phone': repair_obj.client_phone,
			'client_mobile': repair_obj.client_mobile,
			'client_email': repair_obj.client_email,
			'machine_repair_id': repair_obj.id,
			'state': 'draft',
		}
		diagnose_id = Diagnosis_obj.create(diagnose_vals)
		for line in repair_obj.machine_repair_line:
			machine_line_vals = {
				'machine_id': line.machine_id.id,
				'machine_name': line.machine_name,
				'model_number': line.model_number,
				'machine_serial': line.machine_serial,
				'serial_no': line.serial_no.id,
				'service_type': line.service_type.id,
				'guarantee': line.guarantee,
				'guarantee_type':line.guarantee_type,
				'service_detail': line.service_detail,
				'diagnose_id': diagnose_id.id,
				'state': 'diagnosis',
				'source_line_id': line.id,
			}
			Machine_line_obj.create(machine_line_vals)
			line.write({'state': 'diagnosis'})
		
		
		self.write({'state': 'diagnosis', 'diagnose_id': diagnose_id.id})
		result = mod_obj.get_object_reference('machine_repair_industry', 'action_machine_diagnose_tree_view')
		id = result and result[1] or False
		result = act_obj.sudo().browse(id).read()
		res = mod_obj.sudo().get_object_reference('machine_repair_industry', 'view_machine_diagnose_form')
		result[0]['views'] = [(res and res[1] or False, 'form')]
		result[0]['res_id'] = diagnose_id.id or False
		return result

	
	def action_print_receipt(self):
		return self.env.ref('machine_repair_industry.machine_repair_receipt_id').report_action(self)

	
	def action_print_label(self):
		return self.env.ref('machine_repair_industry.machine_repair_label_id').report_action(self)

	def action_done(self):
		self.write({'state':'done'})


	def action_view_quotation(self):
		mod_obj = self.env['ir.model.data']
		act_obj = self.env['ir.actions.act_window']
		if self.ids:
			order_id = self.browse(self.ids[0]).sale_order_id.id
		result = mod_obj.get_object_reference('sale', 'action_orders')
		id = result and result[1] or False
		result = act_obj.sudo().browse(id).read()[0]
		res = mod_obj.sudo().get_object_reference('sale', 'view_order_form')
		result['views'] = [(res and res[1] or False, 'form')]
		result['res_id'] = order_id or False
		return result

	
	def action_view_work_order(self):
		mod_obj = self.env['ir.model.data']
		act_obj = self.env['ir.actions.act_window']
		if self.ids:
			work_order_id = self.browse(self.ids[0]).workorder_id.id
		result = mod_obj.get_object_reference('machine_repair_industry', 'action_machine_workorder_tree_view')
		id = result and result[1] or False
		result = act_obj.sudo().browse(id).read()[0]
		res = mod_obj.sudo().get_object_reference('machine_repair_industry', 'view_machine_workorder_form')
		result['views'] = [(res and res[1] or False, 'form')]
		result['res_id'] = work_order_id or False
		return result

class service_type(models.Model):
	_name = 'service.type'
		
	name = fields.Char(string='Name')

class machine_repair_line(models.Model):
	_name = 'machine.repair.line'

	model_number = fields.Char(string='Model #')
	machine_id = fields.Many2one('product.product', string='Machine')
	machine_name = fields.Char(string='Machine Name')
	machine_serial = fields.Char(string='Machine Serial Number')
	serial_no = fields.Many2one('stock.production.lot', string='Serial Number')
	guarantee = fields.Selection(
		[('yes', 'Yes'), ('no', 'No')], string='Under Guarantee?')
	guarantee_type = fields.Selection(
		[('paid', 'paid'), ('free', 'Free')], string='Guarantee Type')
	service_type = fields.Many2one('service.type', string='Nature of Service')
	machine_repair_id = fields.Many2one('machine.repair', string='Machine', copy=False)
	service_detail = fields.Text(string='Service Details')
	diagnostic_result = fields.Text(string='Diagnostic Result')
	diagnose_id = fields.Many2one('machine.diagnose', string='Machine Diagnose', copy=False)
	workorder_id = fields.Many2one('machine.workorder', string='Machine Work Order', copy=False)
	source_line_id = fields.Many2one('machine.repair.line', string='Source')
	est_ser_hour = fields.Float(string='Estimated Sevice Hours')
	service_product_id = fields.Many2one('product.product', string='Service Product')
	service_product_price = fields.Float('Service Product Price')
	spare_part_ids = fields.One2many('spare.part.line', 'machine_id', string='Spare Parts Needed')
	state = fields.Selection([
		('draft', 'Draft'),
		('diagnosis', 'In Diagnosis'),
		('done', 'Done'),
		], 'Status', readonly=True, copy=False, help="Gives the status of the machine Diagnosis.", index=True, default='draft')

	_rec_name = 'machine_id'
	
	@api.model
	def create(self, vals):
		if not vals.get('serial_no') and vals.get('machine_id'):
			lot_vals = {
				'product_id': vals.get('machine_id'),
			}
			lot_id = self.env['stock.production.lot'].create(lot_vals)
			vals.update({'serial_no': lot_id.id})
		return super(machine_repair_line, self).create(vals)

	@api.onchange('service_product_id')
	def onchange_service_price(self):
		if self.service_product_id:
			product = self.env['product.product'].search([('id', '=', self.service_product_id.id)])
			self.service_product_price = product.lst_price
		else:
			self.service_product_price = 0.00

	@api.depends('machine_id', 'machine_name')
	def name_get(self):
		res = []
		for record in self:
			name = record['machine_name']
			if record['machine_id']:
				name = record['machine_id']
			res.append((record['id'], name))
		return res
		
	
	def action_add_machine_diagnosis_result(self):
		if self._ids:
			self.write({'state': 'done'})
			for obj in self.browse(self._ids):
				obj.source_line_id.write({'state': 'done'})
		return True

class machine_repair_analysis(models.Model):
	_name = 'machine.repair.analysis'
	_auto = False
	
	id = fields.Integer('Machine Id', readonly=True)
	sequence = fields.Char(string='Sequence', readonly=True)
	receipt_date = fields.Date(string='Date of Receipt', readonly=True)
	state = fields.Selection([
		('draft', 'Received'),
		('diagnosis', 'In Diagnosis'),
		('diagnosis_complete', 'Diagnosis Complete'),
		('quote', 'Quotation Sent'),
		('saleorder', 'Quotation Approved'),
		('workorder', 'Work in Progress'),
		('work_completed', 'Work Completed'),
		('invoiced', 'Invoiced'),
		('done', 'Done'),
		('cancel', 'Cancelled'),
		], 'Status', readonly=True, copy=False, help="Gives the status of the machine repairing.", index=True)
	client_id = fields.Many2one('res.partner', string='Client', readonly=True)

	_order = 'id desc'

	@api.model
	def init(self):
		cr = self._cr
		tools.drop_view_if_exists(cr, 'machine_repair_analysis')
		cr.execute("""
			create or replace view machine_repair_analysis as (
			select
				mr.id as id,
				mr.sequence as sequence,
				mr.receipt_date as receipt_date,
				mr.state as state,
				mr.client_id as client_id
			from
				machine_repair mr
			group by mr.id,
				mr.receipt_date,
				mr.state,
				mr.client_id
			)
		""")

class ResPartner(models.Model):
	_inherit = 'res.partner'
	
	repair_order_count = fields.Integer(compute='_compute_repair_order_count', string='# of Repair Order')
	
	
	def _compute_repair_order_count(self):
		for partner in self:
			repair_order_ids = self.env['machine.repair'].search([('client_id', '=', partner.id)])            
			partner.repair_order_count = len(repair_order_ids)
			
	
	def button_view_repair(self):
		list = []
		context = dict(self._context or {})
		repair_order_ids = self.env['machine.repair'].search([('client_id', '=', self.id)])         
		for order in repair_order_ids:
			list.append(order.id)
		return {
			'name': _('Machine Repair'),
			'view_type': 'form',
			'view_mode': 'tree,form',
			'res_model': 'machine.repair',
			'view_id': False,
			'type': 'ir.actions.act_window',
			'domain': [('id', 'in',list )],
			'context': context,
		}         
			
