# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class popup_wizard_fail(models.TransientModel):
    _name="popup.wizard.fail"

    test_name = fields.Text(string="Test Connection Fail",readonly=True)
     