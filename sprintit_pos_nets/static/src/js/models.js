odoo.define('sprintit_pos_nets.models', function (require) {
    var models = require('point_of_sale.models');
    var PaymentNetsCloud = require('sprintit_pos_nets.payment');

    models.register_payment_method('nets_cloud', PaymentNetsCloud);
    models.load_fields('pos.payment.method', ['nets_api_token','nets_api_url','nets_username','nets_password']);

    var _paylineproto = models.Paymentline.prototype;
    models.Paymentline = models.Paymentline.extend({
        init_from_JSON: function (json) {
            _paylineproto.init_from_JSON.apply(this, arguments);
            this.nets_payment_response = json.nets_payment_response;
        },
        export_as_JSON: function () {
            return _.extend(_paylineproto.export_as_JSON.apply(this, arguments), {
                nets_payment_response: this.nets_payment_response
            });
        }
    });
});
