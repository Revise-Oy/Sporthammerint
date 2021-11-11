odoo.define('sprintit_pos_nets.payment', function (require) {
"use strict";

var core = require('web.core');
var rpc = require('web.rpc');
var PaymentInterface = require('point_of_sale.PaymentInterface');

var _t = core._t;

var PaymentNetsCloud = PaymentInterface.extend({
    init: function () {
        this._super.apply(this, arguments);
    },
    send_payment_request: function () {
        this._super.apply(this, arguments);
        return this._nets_cloud_pay();
    },
    send_payment_cancel: function () {
        this._super.apply(this, arguments);
        return this._nets_cloud_cancel();
    },
    close: function () {
        this._super.apply(this, arguments);
    },

    _nets_cloud_pay: async function () {
        // Send payment transaction to Nets Cloud / payment terminal
        const order = this.pos.get_order()
        const payment_line = order.selected_paymentline;
        const config = this.pos.config;
        const payment_method = this.payment_method;

        // Normal purchase when amount > 0 otherwise it's a refund / return of goods
        const payment_type = payment_line.amount > 0 ? 'purchase' : 'returnOfGoods';
        const payment_amount = payment_type == 'returnOfGoods' ? payment_line.amount * -1 : payment_line.amount;

        // Use existing token or log in if needed
        this._nets_authenticate();

        // Waiting for card
        payment_line.set_payment_status('waitingCard');

        // Send payment transaction to payment terminal
        const raw_purchase_reponse = await fetch(payment_method.nets_api_url+'/v1/terminal/'+config.nets_terminal_id+'/transaction', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'bearer '+payment_method.nets_api_token
            },
            body: JSON.stringify(
                {
                    "transactionType": payment_type,
                    "amount": Math.round(payment_amount*100),
                    "allowPinBypass": false
                }
            )
        });

        const purchase_reponse = await raw_purchase_reponse.json();

        if (raw_purchase_reponse.ok) {
            // Payment successful
            payment_line.set_receipt_info(this._gather_customer_receipt(purchase_reponse));
            payment_line.nets_payment_response = purchase_reponse;
            payment_line.card_type = purchase_reponse['result'][0]['cardType'];
            payment_line.transaction_id = purchase_reponse['result'][0]['transactionId'];
            payment_line.paid = true;
            return true;
        }
        else {
            // Payment failed
            this._show_error(_('Payment error:')+'\n\n'+purchase_reponse['failure']['error']);
            return false;
        }
    },

    _nets_cloud_cancel: async function () {
        // Called when a user removes a payment line that's still waiting
        // on send_payment_request to complete
        const config = this.pos.config;
        const payment_method = this.payment_method;

        // Use existing token or log in if needed
        this._nets_authenticate();

        const raw_cancel_reponse = await fetch(payment_method.nets_api_url+'/v1/terminal/'+config.nets_terminal_id+'/administration', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'bearer '+payment_method.nets_api_token
            },
            body: JSON.stringify(
                {
                    "action": "cancelAction"
                }
            )
        });

        if (!raw_cancel_reponse.ok) {
            // Cancel failed
            this._show_error(_('Cancelling Nets payment failed. Please cancel it manually.'));
            return false;
        }
    },

    _nets_authenticate: async function () {
        // Use exisiting token for authorization
        // or log in if token is not valid or missing
        var login_ok = false;
        const payment_method = this.payment_method;
        const config = this.pos.config;

        if (payment_method.nets_api_token) {
            // Try existing token to see if it's still valid
            const raw_terminals_reponse = await fetch(payment_method.nets_api_url+'/v1/terminal/', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': 'bearer '+payment_method.nets_api_token
                }
            });

            if (raw_terminals_reponse.ok) {
                const terminals_reponse = await raw_terminals_reponse.json();

                if (terminals_reponse['terminals'].length > 0) {
                    // Also check that the current terminal id is included in the allowed terminals list
                    function checkTerminal(terminal) {
                        return terminal['terminalId'] == config.nets_terminal_id;
                    }
                    const terminalId = terminals_reponse['terminals'].filter(checkTerminal);

                    if (terminalId.length == 1) {
                        login_ok = true;
                    }
                    else {
                        this._show_error(_('Nets terminal ID invalid!'));
                        return false;
                    }
                }
            }
        }

        if (!login_ok) {
            // Log in and fetch new token, if needed
            payment_method.nets_api_token = await this._nets_login();
        }
    },

    _nets_login: async function () {
        // Log in and fetch new token
        const config = this.pos.config;
        const payment_method = this.payment_method;

        const raw_login_response = await fetch(payment_method.nets_api_url+'/v1/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(
                {
                    "username": payment_method.nets_username,
                    "password": payment_method.nets_password,
                }
            )
        });
        const login_response = await raw_login_response.json();

        // Check that session terminal id is included in allowed terminals
        if (!login_response['terminals'].includes(config.nets_terminal_id)) {
            this._show_error("Nets terminal ID invalid!");
        }

        if (!login_response['token']) {
            this._show_error("Nets login failed!");
        }

        const res = await rpc.query({
            model: 'pos.payment.method',
            method: 'set_nets_api_token',
            args: [
                payment_method.id,
                login_response['token'],
            ]
        });

        return login_response['token']
    },

    _show_error: function (msg, title) {
        // Show error message
        if (!title) {
            title =  _t('Nets Cloud@Connect Error');
        }
        this.pos.gui.show_popup('error',{
            'title': title,
            'body': msg,
        });
    },

    _gather_customer_receipt: function (purchase_reponse) {
        // Gather the customer receipt text from the purchase transaction response
        var customer_receipt_text = '';
        _.each(purchase_reponse['result'], function(result) {
            customer_receipt_text = result['customerReceipt'];
        });
        return customer_receipt_text.replace(/\n/g, "<br />");
    }
});

return PaymentNetsCloud;
});
