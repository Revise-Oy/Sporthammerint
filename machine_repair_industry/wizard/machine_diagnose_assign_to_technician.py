# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _
from odoo import tools
from odoo.exceptions import UserError
from odoo.exceptions import Warning


class machine_diagnose_assignto_technician(models.TransientModel):
    _name = 'machine.diagnose.assignto.technician'

    user_id = fields.Many2one('res.users', string='Technician', required=True)

    
    def do_assign_technician(self):
        wiz_obj = self.browse(self._ids[0])
        if wiz_obj.user_id and self._context.get('active_id'):
            self.env['machine.diagnose'].browse(self._context.get('active_id')).write({'user_id': wiz_obj.user_id.id, 'state': 'in_progress'})
        return {'type': 'ir.actions.act_window_close'}
