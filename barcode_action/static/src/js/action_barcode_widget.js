odoo.define('barcode_action.field', function (require) {
    "use strict";

    var AbstractField = require('web.AbstractField');
    var field_registry = require('web.field_registry');

    var ActionBarcodeField = AbstractField.extend({
        init: function () {
            this._super.apply(this, arguments);
            this.trigger_up('activeBarcode', {
                name: this.name,
                commands: {
                    barcode: '_barcodeHandleAction',
                },
            });
        },
    });
    field_registry.add('action_barcode_handler', ActionBarcodeField);

    return {
        ActionBarcodeField:ActionBarcodeField,
    };

});
