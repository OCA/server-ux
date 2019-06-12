odoo.define('barcode_action.form', function (require) {
    "use strict";

    var FormController = require('web.FormController');

    FormController.include({
        _barcodeHandleAction: function (barcode, activeBarcode) {
            var record = this.model.get(this.handle);
            var self = this;
            return self._rpc({
                    model: record.data.model,
                    method: record.data.method,
                    args: [[record.data.res_id], barcode],
                }).done(function (action) {
                    if (action) {
                        self._barcodeStopListening();
                        self.do_action(action);
                    }
                });
        },
    });

});
