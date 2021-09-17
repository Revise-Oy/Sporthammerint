# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT

class SaleOrder(models.Model):
	_inherit = 'sale.order'

	diagnose_id = fields.Many2one('machine.diagnose', string='Machine Diagnosis', )
	machine_repair_id  = fields.Many2one('machine.repair',string='Machine Repair',)
	workorder_id = fields.Many2one('machine.workorder', string='Repair Work Order', )
	is_workorder_created = fields.Boolean(string = "Workorder Created")
	count_machine_repair  = fields.Integer(string='Repair Orders', compute='_compute_repair_id')
	workorder_count = fields.Integer(string='Work Orders', compute='_compute_workorder_id')
	machine_repair_line_id  = fields.Many2one('machine.repair.line',string='Machine Repair Line',)

	
	@api.depends('machine_repair_id')
	def _compute_repair_id(self):
		for order in self:
			repair_order_ids = self.env['machine.repair'].search([('sale_order_id', '=', order.id)])            
			order.count_machine_repair = len(repair_order_ids)

	
	@api.depends('is_workorder_created')
	def _compute_workorder_id(self):
		for order in self:
			work_order_ids = self.env['machine.workorder'].search([('sale_order_id', '=', order.id)])            
			order.workorder_count = len(work_order_ids)

	
	def workorder_created(self):
		self.write({'state':'workorder'})

	
	def action_confirm(self):
		Machine_line_obj = self.env['machine.repair.line']
		if  self.diagnose_id:
			wo_vals = {
					'name': self.diagnose_id.name,
					'client_id': self.diagnose_id.client_id.id,
					'sale_order_id': self.id,
					'machine_repair_id': self.diagnose_id.machine_repair_id.id,
					'diagnose_id': self.diagnose_id.id,
					'hour': sum((line.est_ser_hour for line in self.diagnose_id.machine_repair_line), 0.0),
					'priority': self.diagnose_id.priority,
					'state': 'draft',
					'confirm_sale_order' : True,
				}
			wo_id = self.env['machine.workorder'].create(wo_vals)
			for line in self.diagnose_id.machine_repair_line:
				machine_line_vals = {
						'workorder_id': wo_id,
					}
				line.write({'workorder_id':wo_id.id})
				Machine_line_obj.write({'machine_repair_line': line.id})
			diag_id = self.diagnose_id.id
			diagnose_obj = self.env['machine.diagnose'].browse(diag_id)
			diagnose_obj.is_workorder_created = True
			diagnose_obj.confirm_sale_order = True
			if diagnose_obj.machine_repair_id:
				repair_id = [diagnose_obj.machine_repair_id.id]
				browse_record_machine_rpr = self.env['machine.repair'].browse(repair_id)
				browse_record_machine_rpr.state = 'saleorder'
				browse_record_machine_rpr.workorder_id = wo_id
				browse_record_machine_rpr.confirm_sale_order = True 
				self.write({'workorder_id': wo_id.id,'machine_repair_id':diagnose_obj.machine_repair_id.id, 'is_workorder_created':True})
		res = super(SaleOrder, self).action_confirm()
		return res

	
	def button_view_repair(self):
		list = []
		context = dict(self._context or {})
		repair_order_ids = self.env['machine.repair'].search([('sale_order_id', '=', self.id)])         
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

	
	def button_view_workorder(self):
		list = []
		context = dict(self._context or {})
		work_order_ids = self.env['machine.workorder'].search([('sale_order_id', '=', self.id)])           
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

	
	def action_view_work_order(self):
		mod_obj = self.env['ir.model.data']
		act_obj = self.env['ir.actions.act_window']
		if self._ids:
			work_order_id = self.workorder_id.id
		result = mod_obj.get_object_reference('machine_repair_industry', 'action_machine_workorder_tree_view')
		id = result and result[1] or False
		result = act_obj.sudo().browse(id).read()[0]
		res = mod_obj.sudo().get_object_reference('machine_repair_industry', 'view_machine_workorder_form')
		result['views'] = [(res and res[1] or False, 'form')]
		result['res_id'] = work_order_id or False
		return result


class sale_advance_payment_inv(models.TransientModel):
	_inherit = "sale.advance.payment.inv"
	_description = "Sales Advance Payment Invoice"

	def create_invoices(self):

		sale_orders = self.env['sale.order'].browse(self._context.get('active_ids', []))
		if self.advance_payment_method == 'delivered' :
			if sale_orders.diagnose_id and sale_orders.diagnose_id.machine_repair_id:
				sale_orders.diagnose_id.machine_repair_id.write( {'state': 'invoiced'})
				sale_orders.diagnose_id.machine_repair_id.diagnose_id.write({'is_invoiced': True})
			sale_orders._create_invoices(final=self.deduct_down_payments)

			if self._context.get('open_invoices', False):
				return sale_orders.action_view_invoice()
			return {'type': 'ir.actions.act_window_close'}

		return super(sale_advance_payment_inv, self).create_invoices()


class AccountInvoice(models.Model):
	_inherit = 'account.move'
	
	create_form_machine = fields.Boolean(string='Machine')
	
	@api.model
	def create(self, vals):
		if vals.get('invoice_origin'):
			sale_obj = self.env['sale.order'].search([('name', '=', vals.get('invoice_origin'))])
			if sale_obj  and sale_obj.workorder_id and sale_obj.workorder_id.machine_repair_id:
				vals.update({'create_form_machine': True})
		return super(AccountInvoice, self).create(vals)

	
	def write(self,vals):
		if vals.get('state'):
			if vals.get('state') == 'paid':
				sale_obj = self.env['sale.order'].search([('name', '=', self.origin)])
				if sale_obj  and sale_obj.workorder_id and sale_obj.workorder_id.machine_repair_id:
					repair_obj = self.env['machine.repair'].search([('id', '=', sale_obj.workorder_id.machine_repair_id.id)])
					repair_obj.write({'state': 'done'})
		return super(AccountInvoice, self).write(vals)


class ProductTemplate(models.Model):
	_inherit = 'product.template'
	
	machine = fields.Boolean(string='Machine')



class mail_compose_message(models.TransientModel):
	_inherit = 'mail.compose.message'
	
	def send_mail(self, auto_commit=False):
		if self._context.get('default_model') == 'sale.order' and self._context.get('default_res_id') and self._context.get('mark_so_as_sent'):
			order = self.env['sale.order'].browse([self._context['default_res_id']])
			if order.diagnose_id and order.diagnose_id.machine_repair_id:
				order.diagnose_id.machine_repair_id.write({'state': 'quote'})
			self = self.with_context(mail_post_autofollow=True)
		return super(mail_compose_message, self).send_mail(auto_commit=auto_commit)


class SaleOrderLine(models.Model):
	_inherit = 'sale.order.line'
	
	machine_name = fields.Char(string="Machine")
	machine_model = fields.Char(string="Model #")
	
	def _prepare_invoice_line(self, **optional_values):
		res = super(SaleOrderLine, self)._prepare_invoice_line()
		res.update({
			'machine_name' : self.machine_name,
			'machine_model' : self.machine_model
		})
		return res

	
class AccountInvoiceLine(models.Model):
	_inherit = 'account.move.line'
	
	machine_name = fields.Char(string="Machine")
	machine_model = fields.Char(string="Model #")            

