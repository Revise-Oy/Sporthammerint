# -*- coding: utf-'8' "-*-"
# Part of Kanak Infosystems LLP. See LICENSE file for full copyright and licensing details.

import logging

from odoo import api, fields, models, _
from odoo.addons.payment.models.payment_acquirer import ValidationError
from odoo.tools.pycompat import to_text

_logger = logging.getLogger(__name__)


class PaytrailTransaction(models.Model):
    _inherit = 'payment.transaction'

    paytrail_auth_hash = fields.Char('Auth Hash', help='Returned in the transaction response.')
    paytrail_payment_method = fields.Selection([
        ("1", "Nordea"), ("2", "Osuuspankki"), ("3", "Danske Bank"), ("5", "Ålandsbanken"),
        ("6", "Handelsbanken"), ("9", "PayPal"), ("10", "S-Pankki"), ("18", "Jousto"), ("50", "Aktia"),
        ("51", "POP Pankki"), ("52", "Säästöpankki"), ("53", "Visa (Nets)"), ("54", "MasterCard (Nets)"),
        ("55", "Diners Club (Nets)"), ("56", "American Express (Nets)"), ("58", "MobilePay"),
        ("60", "Collector Bank"), ("61", "Oma Säästöpankki"), ("11", "Klarna Invoice"),
        ("12", "Klarna Installment"), ("30", "Visa"), ("31", "MasterCard"), ("34", "Diners Club"), ("35", "JCB")], string='Payment Method')

    @api.model
    def _paytrail_form_get_tx_from_data(self, data):
        reference = data.get('ORDER_NUMBER')
        if not reference:
            error_msg = 'Paytrail: received data with missing order reference (%s)' % (reference)
            _logger.error(error_msg)
            raise ValidationError(error_msg)
        tx = self.env['payment.transaction'].search([('reference', '=', reference)])
        if not tx or len(tx) > 1:
            error_msg = 'Paytrail: received data for reference %s' % (reference)
            if not tx:
                error_msg += ': no order found'
            else:
                error_msg += ': multiple order found'
            _logger.info(error_msg)
            raise ValidationError(error_msg)

        # verify shasign
        if tx.acquirer_id.paytrail_version_type == 'E2':
            shasign_check = tx.acquirer_id.get_paytrail_e2_authcode('out', data)
            if to_text(shasign_check) != to_text(data.get('RETURN_AUTHCODE')):
                error_msg = _('Paytrail: invalid RETURN_AUTHCODE, received %s, computed %s') % (data.get('RETURN_AUTHCODE'), shasign_check)
                _logger.warning(error_msg)
                raise ValidationError(error_msg)
        return tx

    def _paytrail_form_get_invalid_parameters(self, data):
        invalid_parameters = []
        # Check reference order number
        if self.acquirer_id.paytrail_version_type == 'E1':
            if self.acquirer_reference and data.get('PAID') != self.acquirer_reference:
                invalid_parameters.append(('Paytrail PAID Number', data.get('PAID'), self.acquirer_reference))
        else:
            if self.acquirer_reference and data.get('PAYMENT_ID') != self.acquirer_reference:
                invalid_parameters.append(('Paytrail PAYMENT ID', data.get('PAYMENT_ID'), self.acquirer_reference))
        return invalid_parameters

    def _paytrail_form_validate(self, data):
        if self.acquirer_id.paytrail_version_type == 'E1':
            response = data.get('PAID')
            if response:
                _logger.info('Paytrail payment for tx %s: set as done' % (self.reference))
                self.write({
                    'acquirer_reference': response,
                    'date': fields.Datetime.now(),
                    'paytrail_payment_method': data.get('METHOD') if self.acquirer_id.paytrail_version_type == 'E1' else data.get('PAYMENT_METHOD'),
                    'paytrail_auth_hash': data.get('RETURN_AUTHCODE')
                })
                self._set_transaction_done()
            else:
                error = 'Received unrecognized response for Paytrail Payment %s, set as error' % (self.reference)
                _logger.info(error)
                self.write({
                    'date': fields.Datetime.now(),
                    'paytrail_auth_hash': data.get('RETURN_AUTHCODE'),
                    'state_message': error
                })
                self._set_transaction_cancel()
        else:
            status = data.get('STATUS')
            self.write({
                'acquirer_reference': data.get('PAYMENT_ID'),
                'date': fields.Datetime.now(),
                'paytrail_payment_method': data.get('PAYMENT_METHOD'),
                'paytrail_auth_hash': data.get('RETURN_AUTHCODE'),
            })
            if status == 'PAID':
                _logger.info('Paytrail payment for tx %s: set as DONE' % (self.reference))
                self._set_transaction_done()
            elif status == 'CANCELLED':
                _logger.info('Paytrail payment for tx %s: set as CANCELLED' % (self.reference))
                self._set_transaction_cancel()
            else:
                error = 'Received unrecognized response for Paytrail Payment %s, set as error' % (self.reference)
                _logger.info(error)
                self.write({
                    'state_message': error
                })
                self._set_transaction_error(error)
