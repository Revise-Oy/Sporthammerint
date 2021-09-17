# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _

class machine_diagnose(models.Model):
    _name = 'machine.diagnose'
    _inherit = ['mail.thread']

    name = fields.Char(string='Subject', required=True)
    service_rec_no = fields.Char(string='Receipt No', readonly=True)
    client_id = fields.Many2one('res.partner', string='Client', required=True)
    client_phone = fields.Char(string='Phone')
    client_mobile = fields.Char(string='Mobile')
    client_email = fields.Char(string='Email')
    receipt_date = fields.Date(string='Date of Receipt')
    contact_name = fields.Char(string='Contact Name')
    phone = fields.Char(string='Contact Number')
    machine_id = fields.Many2one('product.product', string='Machine')
    model_number = fields.Char(string='Model #')
    machine_name = fields.Char(string='Machine Name')
    serial_no = fields.Many2one('stock.production.lot', string='Serial Number')
    service_type = fields.Many2one('service.type', string='Nature of Service')
    user_id = fields.Many2one('res.users', string='Technician')
    priority = fields.Selection([('0','Low'), ('1','Normal'), ('2','High')], 'Priority')
    description = fields.Text(string='Fault Description')
    spare_part_ids = fields.One2many('spare.part.line', 'diagnose_id', string='Spare Parts Needed')
    est_ser_hour = fields.Float(string='Estimated Sevice Hours')
    service_product_id = fields.Many2one('product.product', string='Service Product')
    service_product_price = fields.Integer('Service Product Price')
    machine_repair_id = fields.Many2one('machine.repair', string='Source', copy=False)
    sale_order_id = fields.Many2one('sale.order', string='Sales Order', copy=False)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('done', 'Complete'),
        ], 'Status', readonly=True, copy=False, help="Gives the status of the machine Diagnosis.", index=True, default='draft')
    machine_repair_line = fields.One2many('machine.repair.line', 'diagnose_id', string="Machine Lines")
    machine_repair_count  = fields.Integer(string='Repair Orders', compute='_compute_repair_id')
    workorder_count = fields.Integer(string='Work Orders', compute='_compute_workorder_id')
    is_workorder_created = fields.Boolean(string = "Workorder Created")
    confirm_sale_order = fields.Boolean(string = "confirm sale order")
    is_invoiced = fields.Boolean(string = "invoice Created", default  = False)
    quotation_count = fields.Integer(string ="Quotations", compute='_compute_quotation_id')
    saleorder_count = fields.Integer(string = "Sale Order", compute='_compute_saleorder_id')
    inv_count = fields.Integer(string = "Invoice")
 
    
    @api.depends('machine_repair_id')
    def _compute_repair_id(self):
        for order in self:
            repair_order_ids = self.env['machine.repair'].search([('diagnose_id', '=', order.id)])            
            order.machine_repair_count = len(repair_order_ids)

    
    @api.depends('is_workorder_created')
    def _compute_workorder_id(self):
        for order in self:
            work_order_ids = self.env['machine.workorder'].search([('diagnose_id', '=', order.id)])            
            order.workorder_count = len(work_order_ids)

    
    @api.depends('sale_order_id')
    def _compute_quotation_id(self):
        for order in self:
            if order:
                quo_order_ids = self.env['sale.order'].search([('state', '=', 'draft'),('machine_repair_id.diagnose_id.id', '=', order.id)])            
                order.quotation_count = len(quo_order_ids)

    
    
    @api.depends('confirm_sale_order')
    def _compute_saleorder_id(self):
        for order in self:
            order.quotation_count = 0
            so_order_ids = self.env['sale.order'].search([('state', '=', 'sale'),('machine_repair_id.diagnose_id.id', '=', order.id)])            
            order.saleorder_count = len(so_order_ids)

    
    @api.depends('is_invoiced')
    def _compute_invoice_id(self):
        count  = 0 
        for order in self:
            so_order_ids = self.env['sale.order'].search([('state', '=', 'sale'),('machine_repair_id.diagnose_id.id', '=', order.id)])
            for order in so_order_ids:
                inv_order_ids = self.env['account.move'].search([('origin', '=',order.name )])            
                if inv_order_ids:
                    self.inv_count = len(inv_order_ids)         
 
    
    def button_view_repair(self):
        list = []
        context = dict(self._context or {})
        repair_order_ids = self.env['machine.repair'].search([('diagnose_id', '=', self.id)])         
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
        work_order_ids = self.env['machine.workorder'].search([('machine_repair_id.diagnose_id', '=', self.id)])           
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
        quo_order_ids = self.env['sale.order'].search([('state', '=', 'draft'),('machine_repair_id.diagnose_id', '=', self.id)])           
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
        quo_order_ids = self.env['sale.order'].search([('state', '=', 'sale'),('machine_repair_id.diagnose_id', '=', self.id)])           
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
        so_order_ids = self.env['sale.order'].search([('state', '=', 'sale'),('machine_repair_id.diagnose_id', '=', self.id)])
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
   
        
    _order = 'id desc'
    
    
    def button_in_progress(self):
        self.write({'state': 'in_progress'})

    
    def button_done(self):
        self.write({'state':'done'})

    
    def button_cancel(self):
        self.write({'state':'cancel'})

    
    def button_draft(self):
        self.write({'state':'draft'})

    @api.onchange('client_id')
    def onchange_partner_id(self):
        addr = {}
        part = self.client_id
        if part:
            part = self.env['res.partner'].browse(part)
            addr = self.env['res.partner'].address_get([part.id], ['contact'])
        return {'value': addr}

    
    def action_create_quotation(self):
        diagnose_obj = self.env['machine.diagnose'].browse(self.ids[0])
        repair_obj = self.env['machine.repair']
        mod_obj = self.env['ir.model.data']
        product_obj = self.env['product.product']
        act_obj = self.env['ir.actions.act_window']
        service_hour = 0.0
        counter = 0
        for machine_line in diagnose_obj.machine_repair_line:
            if machine_line.spare_part_ids:
                counter += 1
        quote_vals = {
            'partner_id': diagnose_obj.client_id.id or False,
            'state': 'draft',
            'client_order_ref': diagnose_obj.name,
            'diagnose_id': diagnose_obj.id,
            'machine_repair_id': diagnose_obj.machine_repair_id.id
        }
        order_id = self.env['sale.order'].create(quote_vals)
        if diagnose_obj.machine_repair_id:
            id = diagnose_obj.machine_repair_id
            id.write({'state': 'diagnosis_complete', 'sale_order_id': order_id.id})


        for machine_line in diagnose_obj.machine_repair_line:
            if machine_line.guarantee == 'no' or machine_line.guarantee == 'yes':
                service_hour += machine_line.est_ser_hour
                if service_hour != 0.0:
                    service_line_vals = {
                        'product_id': machine_line.service_product_id.id,
                        'name': machine_line.service_product_id.name,
                        'product_uom_qty': service_hour,
                        'product_uom': machine_line.service_product_id.uom_id.id,
                        'price_unit' : machine_line.service_product_price,
                        'order_id': order_id.id,
                        'machine_name' : machine_line.machine_name,
                        'machine_model' : machine_line.model_number,
                    }
                    self.env['sale.order.line'].create(service_line_vals)


        for machine_line in diagnose_obj.machine_repair_line:
            if machine_line.guarantee == 'yes':
                for part_line in machine_line.spare_part_ids:
                    line_vals = {
                        'product_id': part_line.product_id.id,
                        'name': part_line.product_id.name,
                        'product_uom_qty': part_line.quantity,
                        'product_uom': part_line.product_id.uom_id.id,
                        'price_unit' : part_line.product_id.lst_price,
                        'order_id': order_id.id,
                        'machine_name' : machine_line.machine_name,
                        'machine_model' : machine_line.model_number,
                    }
                    
                    self.env['sale.order.line'].create(line_vals)
                    
            elif machine_line.guarantee == 'no':
                for part_line in machine_line.spare_part_ids:
                    line_vals = {
                        'product_id': part_line.product_id.id,
                        'name': part_line.product_id.name,
                        'product_uom_qty': part_line.quantity,
                        'product_uom': part_line.product_id.uom_id.id,
                        'price_unit' : part_line.product_id.lst_price,
                        'order_id': order_id.id,
                        'machine_name' : machine_line.machine_name,
                        'machine_model' : machine_line.model_number,
                    }
                    self.env['sale.order.line'].create(line_vals)
        result = mod_obj.get_object_reference('sale', 'action_orders')
        id = result and result[1] or False
        
        result = act_obj.sudo().browse(id).read()[0]
        res = mod_obj.sudo().get_object_reference('sale', 'view_order_form')
        result['views'] = [(res and res[1] or False, 'form')]
        result['res_id'] = order_id.id or False
        self.write({'sale_order_id': order_id.id, 'state': 'done'})
        return result
        
    
    def action_view_sale_order(self):
        mod_obj = self.env['ir.model.data']
        act_obj = self.env['ir.actions.act_window']
        if self:
            order_id = self.sale_order_id.id
        result = mod_obj.get_object_reference('sale', 'action_orders')
        id = result and result[1] or False
        result = act_obj.sudo().browse(id).read()[0]
        res = mod_obj.sudo().get_object_reference('sale', 'view_order_form')
        result['views'] = [(res and res[1] or False, 'form')]
        result['res_id'] = order_id or False
        return result

            
    def action_view_machine_repair(self):
        mod_obj = self.env['ir.model.data']
        act_obj = self.env['ir.actions.act_window']
        if self:
            repair_id = self.machine_repair_id.id
        result = mod_obj.get_object_reference('machine_repair_industry', 'action_machine_repair_tree_view')
        id = result and result[1] or False
        result = act_obj.sudo().browse(id).read()[0]
        res = mod_obj.sudo().get_object_reference('machine_repair_industry', 'view_machine_repair_form')
        result['views'] = [(res and res[1] or False, 'form')]
        result['res_id'] = repair_id or False
        return result

        
class spare_part_line(models.Model):
    _name = 'spare.part.line'

    product_id = fields.Many2one('product.product', string='Product', required=True)
    name = fields.Char(string='Description')
    default_code = fields.Char(string='Product Code')
    uom_id = fields.Many2one('uom.uom', 'Unit of Measure')
    quantity = fields.Float(string='Quantity', required=True)
    price_unit = fields.Float(string='Unit Price')
    diagnose_id = fields.Many2one('machine.diagnose', string='Machine Diagnose')
    workorder_id = fields.Many2one('machine.workorder', string='Machine Workorder')
    machine_id = fields.Many2one('machine.repair.line', string='Machine')
    
    @api.onchange('product_id')
    def onchange_product_id(self):
        res = {}
        product = self.product_id
        if product:
            res = {'default_code': product.default_code,'price_unit': product.lst_price}
        return {'value': res}
