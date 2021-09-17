# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _
from datetime import date, time, datetime
from odoo import tools
from odoo.exceptions import UserError
from odoo.exceptions import Warning


class machine_repair_assign_to_head_tech(models.TransientModel):
    _name = 'machine.repair.assignto.headtech'

    user_id = fields.Many2one('res.users', string='Head Technician', required=True)

    
    def do_assign_ht(self):
        wiz_obj = self.browse(cr, uid, ids[0])
        if wiz_obj.user_id and context.get('active_id'):
            self.env['machine.repair'].write(context.get('active_id'), {'user_id': wiz_obj.user_id.id, 'state': 'confirm'})
        return {'type': 'ir.actions.act_window_close'}
