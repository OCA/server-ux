/** @odoo-module */

import {attr} from "@mail/model/model_field";
import {registerPatch} from "@mail/model/model_core";

registerPatch({
    name: "SuggestedRecipientInfo",
    fields: {
        overrideIsSelected: attr({
            compute() {
                return this.partner ? this.isChecked : false;
            },
            default: false,
        }),
        // We need to define an auxiliary field that allows us to set the default
        // value to false, since overwriting an existing field with this input is
        // not supported: https://github.com/odoo/odoo/blob/518518f53d81d4725babc42b51bfd1336cbf56c9/addons/mail/static/src/model/model_core.js#L310-L311
        isSelected: {
            compute() {
                return this.overrideIsSelected;
            },
        },
    },
});
