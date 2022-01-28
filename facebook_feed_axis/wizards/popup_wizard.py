# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class popup_wizard(models.TransientModel):
    _name="popup.wizard"
    _description = "Message wizard to display warnings, alert ,success messages"      


    name=fields.Text(string="Test Connection Success",readonly=True)
    
   
