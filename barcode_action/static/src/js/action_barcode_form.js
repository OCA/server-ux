odoo.define("barcode_action.form", function (require) {
    "use strict";

    var FormController = require("web.FormController");

    FormController.include({
        _barcodeHandleAction: function (barcode) {
            var record = this.model.get(this.handle);
            var self = this;
            return self
                ._rpc({
                    model: record.data.model,
                    method: record.data.method,
                    args: [[record.data.res_id], barcode],
                })
                .then(function (action) {
                    if (action) {
                        self._barcodeStopListening();
                        self.do_action(action);
                    }
                });
        },
    });
});
