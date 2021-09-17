# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import tools
from odoo import fields, models, api, _


class workorderreport(models.Model):
    _name = "workorder.report.analysis"
    _description = "Sales Orders Statistics"
    _auto = False
    _rec_name = 'date'
    _order = 'date desc'

    name = fields.Char('Work Order', readonly=True)
    date = fields.Date('Date Order', readonly=True)
    date_start = fields.Datetime('Start Date', readonly=True)
    date_finish = fields.Datetime('Finish Date', readonly=True)
    hours_worked = fields.Float(string='Hours Worked')
    product_id = fields.Many2one('product.product','Product', readonly=True)
    #product_uom = fields.Many2one('uom.uom', 'Unit of Measure', readonly=True)
    product_uom_qty = fields.Float('# of Qty', readonly=True)
    partner_id = fields.Many2one('res.partner', 'Partner', readonly=True)
    user_id = fields.Many2one('res.users', 'Salesperson', readonly=True)
    price_total = fields.Float('Total', readonly=True)
    price_subtotal = fields.Float('Untaxed Total', readonly=True)
    product_tmpl_id = fields.Many2one('product.template', 'Product Template', readonly=True)
    categ_id = fields.Many2one('product.category', 'Product Category', readonly=True)
    nbr = fields.Integer('# of Lines', readonly=True)
    country_id = fields.Many2one('res.country', 'Partner Country', readonly=True)
    commercial_partner_id = fields.Many2one('res.partner', 'Commercial Entity', readonly=True)
    delay = fields.Float(string='Working Hours', readonly=True)
    serial_no = fields.Many2one('stock.production.lot', string='Serial Number')
    state = fields.Selection([('draft','Draft'),('cancel','Cancelled'),('pause','Pending'),('startworking', 'In Progress'),('done','Finished')], string='Status', readonly=True)

    def _select(self):
        select_str = """
			SELECT min(mrl.id) as id,
			mrl.machine_id as product_id,
                    mrl.serial_no,
                    spl.quantity  as product_uom_qty,
                    sum(spl.price_unit) as price_total,
                    sum(spl.price_unit) as price_subtotal,
                    count(*) as nbr,
                    m.sequence as name,
                    m.date_start as date_start,
                    m.date_finished as date_finish,
                    m.date as date,
                    m.state as state,
                    m.client_id as partner_id,
                    m.user_id as user_id,
                    m.delay as delay,
                    m.hours_worked as hours_worked,
                    t.categ_id as categ_id,
                    p.product_tmpl_id as product_tmpl_id,
                    partner.country_id as country_id,
                    partner.commercial_partner_id as commercial_partner_id
        """ 
        return select_str

    def _from(self):
        
#        from_str = """
#                sale_order_line l
#                      join sale_order s on (l.order_id=s.id)
#                      join res_partner partner on s.partner_id = partner.id
#                        left join product_product p on (l.product_id=p.id)
#                            left join product_template t on (p.product_tmpl_id=t.id)
#                    left join product_uom u on (u.id=l.product_uom)
#                    left join product_uom u2 on (u2.id=t.uom_id)
#                    left join product_pricelist pp on (s.pricelist_id = pp.id)
#                    left join currency_rate cr on (cr.currency_id = pp.currency_id and
#                        cr.company_id = s.company_id and
#                        cr.date_start <= coalesce(s.date_order, now()) and
#                        (cr.date_end is null or cr.date_end > coalesce(s.date_order, now())))
#        """
#        return from_str
        
        from_str = """
                machine_repair_line mrl
                      join machine_workorder m on (mrl.workorder_id=m.id)
                      join res_partner partner on m.client_id = partner.id
                        left join product_product p on (mrl.service_product_id=p.id)
                        left join spare_part_line spl on (spl.machine_id=mrl.id)
                            left join product_template t on (p.product_tmpl_id=t.id)
                    
        """
        return from_str

    def _group_by(self):
        group_by_str = """GROUP BY mrl.service_product_id,
        			spl.product_id,
        			mrl.machine_id,
        			m.sequence,
        			mrl.serial_no,
        			m.date,
        			m.date_start,
        			m.date_finished,
        			mrl.est_ser_hour,
        			m.delay,
        			spl.quantity,
        			m.hours_worked,
                    t.uom_id,
                    t.categ_id,
                    m.name,
                    m.client_id,
                    m.user_id,
                    m.state,
                    p.product_tmpl_id,
                    partner.country_id,
                    partner.commercial_partner_id
        """
        return group_by_str


    def init(self):
        # self._table = sale_report
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (
            %s
            FROM ( %s )
            %s
            )""" % (self._table, self._select(), self._from(), self._group_by()))
