# -*- coding: utf-'8' "-*-"
# Part of Kanak Infosystems LLP. See LICENSE file for full copyright and licensing details.

import hashlib
import logging
from decimal import *
from werkzeug import urls

from odoo import api, fields, models, _
from odoo.addons.payment_paytrail.controllers.main import PaytrailController
from odoo.exceptions import UserError


_logger = logging.getLogger(__name__)
getcontext().prec = 2


class AcquirerPaytrail(models.Model):
    _inherit = 'payment.acquirer'

    @api.model
    def _get_providers(self):
        providers = super(AcquirerPaytrail, self)._get_providers()
        providers.append(['paytrail', 'Paytrail'])
        return providers

    provider = fields.Selection(selection_add=[('paytrail', 'Paytrail')], ondelete={'paytrail': 'set default'})
    paytrail_merchant_id = fields.Integer(
        'Merchant ID', required_if_provider='paytrail', groups='base.group_user',
        help='Merchant ID is the merchant identification number given by Paytrail.')
    paytrail_merchant_auth_hash = fields.Char(
        'Merchant Hash', required_if_provider='paytrail', groups='base.group_user',
        help='Merchant authentication hash.')
    paytrail_version_type = fields.Selection([('E1', 'E1'), ('E2', 'E2')], string='Interface Version', groups='base.group_user', default='E2')

    @api.onchange('paytrail_version_type')
    def onchange_paytrail_version_type(self):
        self.view_template_id = self.env.ref('payment_paytrail.paytrail_acquirer_button_e1')
        if self.paytrail_version_type:
            if self.paytrail_version_type == 'E2':
                self.view_template_id = self.env.ref('payment_paytrail.paytrail_acquirer_button_e2')
            else:
                self.view_template_id = self.env.ref('payment_paytrail.paytrail_acquirer_button_e1')

    def _get_paytrail_urls(self):
        """ Paytrail URLS """
        return {
            'paytrail_e1_txn_url': 'https://payment.paytrail.com',
            'paytrail_e2_txn_url': 'https://payment.paytrail.com/e2'
        }

    def _get_feature_support(self):
        res = super(AcquirerPaytrail, self)._get_feature_support()
        res['fees'].append('paytrail')
        return res

    def paytrail_compute_fees(self, amount, currency_id, country_id):
        if not self.fees_active:
            return 0.0
        country = self.env['res.country'].browse(country_id)
        if country and self.company_id.country_id.id == country.id:
            percentage = self.fees_dom_var
            fixed = self.fees_dom_fixed
        else:
            percentage = self.fees_int_var
            fixed = self.fees_int_fixed
        fees = (percentage / 100.0 * amount + fixed) / (1 - percentage / 100.0)
        return fees

    def get_paytrail_e1_authcode(self, paytrail_tx_values):
        str = "%s|%s|%s|||%s|%s|%s|||%s|%s||1|||%s|%s|%s|%s|%s||\
%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|0|%s" % (
            self.paytrail_merchant_auth_hash,
            self.paytrail_merchant_id,
            paytrail_tx_values['order_number'],
            paytrail_tx_values['currency_code'],
            paytrail_tx_values['return_url'],
            paytrail_tx_values['cancel_url'],
            paytrail_tx_values['version_type'],
            paytrail_tx_values['culture_lang'],
            paytrail_tx_values['contact_telno'],
            paytrail_tx_values['contact_cellno'],
            paytrail_tx_values['contact_email'],
            paytrail_tx_values['contact_fname'],
            paytrail_tx_values['contact_lname'],
            paytrail_tx_values['contact_add'],
            paytrail_tx_values['contact_zip'],
            paytrail_tx_values['contact_city'],
            paytrail_tx_values['contact_country'],
            paytrail_tx_values['include_vat'],
            paytrail_tx_values['items'],
            paytrail_tx_values['item_title'],
            paytrail_tx_values['item_number'],
            paytrail_tx_values['item_amount'],
            paytrail_tx_values['item_price'],
            paytrail_tx_values['item_tax'],
            paytrail_tx_values['item_type'],
        )

        md5String = hashlib.md5(str.encode('utf-8'))
        hexDig = md5String.hexdigest()
        authCode = hexDig.upper()
        return authCode

    def get_paytrail_e2_authcode(self, inout, values):
        if inout == 'in':
            str = "%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s" % (
                self.paytrail_merchant_auth_hash,
                self.paytrail_merchant_id,
                values['return_url'],
                values['cancel_url'],
                values['notify_url'],
                values['order_number'],
                values['PARAMS_IN'],
                values['PARAMS_OUT'],
                values['order_number'],
                1,
                1,
                values['item_price'],
                0,
                0,
                1,
                values['culture_lang'],
                values['currency_code'],
                values['contact_telno'],
                values['contact_email'],
                values['contact_fname'],
                values['contact_lname'],
                values['company'],
                values['contact_add'],
                values['contact_zip'],
                values['contact_city'],
                values['contact_country'],
                1,
                1
            )
        else:
            str = "%s|%s|%s|%s|%s|%s|%s|%s" % (
                values['ORDER_NUMBER'],
                values['PAYMENT_ID'],
                values['AMOUNT'],
                values['CURRENCY'],
                values['PAYMENT_METHOD'],
                values['TIMESTAMP'],
                values['STATUS'],
                self.paytrail_merchant_auth_hash
            )
        hexDig = hashlib.sha256(str.encode()).hexdigest()
        authCode = hexDig.upper()
        return authCode

    def paytrail_form_generate_values(self, tx_values):
        partner_values = tx_values.get('billing_partner')
        base_url = self.get_base_url()
        if tx_values.get('currency').name != 'EUR':
            raise UserError(_("Paytrail supports only EUR currency !"))
        paytrail_tx_values = dict(tx_values)
        paytrail_tx_values.update({
            'paytrail_merchant_id': self.paytrail_merchant_id,
            'order_number': tx_values.get('reference'),
            'order_desc': '%s: %s' % (self.company_id.name, tx_values.get('reference')),
            'currency_code': tx_values.get('currency') and tx_values.get('currency').name,
            'return_url': '%s' % urls.url_join(base_url, PaytrailController._return_url),
            'cancel_url': '%s' % urls.url_join(base_url, PaytrailController._cancel_url),
            'notify_url': '%s' % urls.url_join(base_url, PaytrailController._notify_url),
            'version_type': self.paytrail_version_type,
            'culture_lang': tx_values.get('partner_lang', 'fi_FI'),
            'mode': 1,
            'contact_telno': partner_values.phone.replace('-', '').replace(' ', '').strip() if partner_values.phone else '1',
            'contact_cellno': partner_values.phone.replace('-', '').replace(' ', '').strip() if partner_values.phone else '1',
            'contact_email': partner_values.email,
            'contact_fname': tx_values.get('partner_first_name', 'first') or 'fname',
            'contact_lname': tx_values.get('partner_last_name', 'last') or 'lname',
            'contact_add': tx_values.get('billing_partner_address', 'address'),
            'contact_zip': tx_values.get('partner_zip'),
            'contact_city': tx_values.get('partner_city'),
            'contact_country': tx_values.get('partner_country', 'NaN') and tx_values.get('partner_country').code,
            'company': self.company_id.name,
            'include_vat': 1,
            'items': 1,
            'item_title': '%s: %s' % (self.company_id.name, tx_values['reference']),
            'item_number': tx_values.get('reference'),
            'item_amount': 1,
            'item_price': Decimal('%.2f' % tx_values.get('amount')),
            'item_tax': 1.00,
            'item_type': 1,
            'vat_cond': False
        })

        if self.paytrail_version_type == 'E1':
            authCode = self.get_paytrail_e1_authcode(paytrail_tx_values)
            paytrail_tx_values['authcode'] = authCode

        elif self.paytrail_version_type == 'E2':
            paytrail_tx_values.update({
                'MSG_UI_MERCHANT_PANEL': tx_values.get('reference'),
                'PARAMS_IN': 'MERCHANT_ID,URL_SUCCESS,URL_CANCEL,URL_NOTIFY,ORDER_NUMBER,PARAMS_IN,PARAMS_OUT,ITEM_TITLE[0],ITEM_ID[0],ITEM_QUANTITY[0],ITEM_UNIT_PRICE[0],ITEM_VAT_PERCENT[0],ITEM_DISCOUNT_PERCENT[0],ITEM_TYPE[0],LOCALE,CURRENCY,PAYER_PERSON_PHONE,PAYER_PERSON_EMAIL,PAYER_PERSON_FIRSTNAME,PAYER_PERSON_LASTNAME,PAYER_COMPANY_NAME,PAYER_PERSON_ADDR_STREET,PAYER_PERSON_ADDR_POSTAL_CODE,PAYER_PERSON_ADDR_TOWN,PAYER_PERSON_ADDR_COUNTRY,VAT_IS_INCLUDED,ALG',
                'PARAMS_OUT': 'ORDER_NUMBER,PAYMENT_ID,AMOUNT,CURRENCY,PAYMENT_METHOD,TIMESTAMP,STATUS'
            })
            authCode = self.get_paytrail_e2_authcode('in', paytrail_tx_values)
            paytrail_tx_values['authcode'] = authCode

        paytrail_tx_values['authcode'] = authCode
        if self.fees_active:
            paytrail_tx_values['handling'] = '%.2f' % paytrail_tx_values.pop('fees', 0.0)
        return paytrail_tx_values

    def paytrail_get_form_action_url(self):
        if self.paytrail_version_type == 'E1':
            return self._get_paytrail_urls()['paytrail_e1_txn_url']
        else:
            return self._get_paytrail_urls()['paytrail_e2_txn_url']
