# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _
from datetime import date, time, datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

class machine_workorder(models.Model):
    _name = 'machine.workorder'
    _inherit = ['mail.thread']
    
    def get_planned_end_date(self):
        res = {}
        for wo_obj in self:
            if wo_obj.date_planned and wo_obj.hour:
                planned_date = datetime.strptime(wo_obj.date_planned, "%Y-%m-%d %H:%M:%S")
                planned_end_date = planned_date + timedelta(hours=wo_obj.hour)
                res[wo_obj.id] = planned_end_date
        return res

    name = fields.Char(string='Work Order', required=True)
    sequence = fields.Char(string='Sequence', readonly=True, default=lambda self: self.env['ir.sequence'].get('machine.workorder'))
    date = fields.Date(string='Date', default=date.today().strftime(DEFAULT_SERVER_DATE_FORMAT))
    client_id = fields.Many2one('res.partner', string='Client', required=True)
    client_phone = fields.Char(string='Phone')
    client_mobile = fields.Char(string='Mobile')
    client_email = fields.Char(string='Email')
    date_planned = fields.Datetime(string='Scheduled Date')
    date_planned_end = fields.Datetime(string='End Date', readonly=True)
    cycle = fields.Float(string='Number of Cycles')
    hour = fields.Float(string='Number of Hours')
    date_start = fields.Datetime(string='Start Date', readonly=True)
    date_finished = fields.Datetime(string='End Date', readonly=True)
    delay = fields.Float(string='Working Hours', readonly=True)
    hours_worked = fields.Float(string='Hours Worked')
    state = fields.Selection([('draft','Draft'),('cancel','Cancelled'),('pause','Pending'),('startworking', 'In Progress'),('done','Finished')],'Status', readonly=True, copy=False,
                             help="* When a work order is created it is set in 'Draft' status.\n" \
                                   "* When user sets work order in start mode that time it will be set in 'In Progress' status.\n" \
                                   "* When work order is in running mode, during that time if user wants to stop or to make changes in order then can set in 'Pending' status.\n" \
                                   "* When the user cancels the work order it will be set in 'Canceled' status.\n" \
                                   "* When order is completely processed that time it is set in 'Finished' status.")
    phone = fields.Char(string='Phone')
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
    machine_repair_id = fields.Many2one('machine.repair', string='Machine Repair', copy=False, readonly=True)
    diagnose_id = fields.Many2one('machine.diagnose', string='Machine Diagnosis', copy=False, readonly=True)
    sale_order_id = fields.Many2one('sale.order', string='Sales Order', copy=False, readonly=True)
    spare_part_ids = fields.One2many('spare.part.line', 'workorder_id', string='Spare Parts')
    machine_repair_line = fields.One2many('machine.repair.line', 'workorder_id', string="Machine Lines")
    count_machine_repair = fields.Integer(string = "Invoice", compute='_compute_machine_repair_id')
    count_dig = fields.Integer(string = "Invoice", compute='_compute_dig_id')
    confirm_sale_order = fields.Boolean('is confirm')
    saleorder_count = fields.Integer(string = "Sale Order", compute='_compute_saleorder_id')
    
    
    @api.depends('machine_repair_id')
    def _compute_machine_repair_id(self):
        for order in self:
            repair_order_ids = self.env['machine.repair'].search([('workorder_id', '=', order.id)])            
            order.count_machine_repair = len(repair_order_ids)

    
    @api.depends('diagnose_id')
    def _compute_dig_id(self):
        for order in self:
            work_order_ids = self.env['machine.diagnose'].search([('machine_repair_id.workorder_id', '=', order.id)])            
            order.count_dig = len(work_order_ids)
            
    
    @api.depends('confirm_sale_order')
    def _compute_saleorder_id(self):
        for order in self:
            so_order_ids = self.env['sale.order'].search([('state', '=', 'sale'),('workorder_id', '=', order.id)])            
            order.saleorder_count = len(so_order_ids)
            
    
    def button_view_repair(self):
        list = []
        context = dict(self._context or {})
        repair_order_ids = self.env['machine.repair'].search([('workorder_id', '=', self.id)])         
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


    
    def button_view_diagnosis(self):
        list = []
        context = dict(self._context or {})
        dig_order_ids = self.env['machine.diagnose'].search([('machine_repair_id.workorder_id', '=', self.id)])           
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

    
    def button_view_saleorder(self):
        list = []
        context = dict(self._context or {})
        order_ids = self.env['sale.order'].search([('state', '=', 'sale'),('workorder_id', '=', self.id)])           
        for order in order_ids:
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
        
    _order = 'id desc'

    
    def button_cancel(self):
        self.write({'state': 'cancel'})

    
    def button_resume(self):
        self.write({'state': 'startworking'})

    
    def button_pause(self):
        self.write({'state': 'pause'})

    
    def button_draft(self):
        self.write({'state': 'draft'})
    
    
    def action_start_working(self):
        self.write({'state':'startworking', 'date_start': datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')})
        if self.machine_repair_id:
            self.machine_repair_id.write({'state': 'workorder'})
        return True

    
    def action_done(self):
        delay = 0.0
        date_now = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')

        date_start = datetime.strptime(str(self.date_start),'%Y-%m-%d %H:%M:%S')
        date_finished = datetime.strptime(date_now,'%Y-%m-%d %H:%M:%S')
        delay += (date_finished-date_start).days * 24
        delay += (date_finished-date_start).seconds / float(60*60)

        self.write({'state':'done', 'date_finished': date_now, 'delay':delay})
        if self.sale_order_id:
            self.sale_order_id.write({'state': 'sale'})
        if self.machine_repair_id:
            self.machine_repair_id.write({'state': 'work_completed'})
        return True

