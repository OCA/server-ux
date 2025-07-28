/** @odoo-module **/

import {registry} from "@web/core/registry";
import {standardFieldProps} from "@web/views/fields/standard_field_props";
import {useBus, useService} from "@web/core/utils/hooks";

import {Component, xml} from "@odoo/owl";

export class ActionBarcodeField extends Component {
    setup() {
        const barcode = useService("barcode");
        this.orm = useService("orm");
        useBus(barcode.bus, "barcode_scanned", this.onBarcodeScanned);
    }

    async onBarcodeScanned(event) {
        const {barcode} = event.detail;
        const record = this.props.record;

        const action = await this.orm.call(
            record.data.model,
            record.data.method,
            [[record.data.res_id], barcode],
            {
                context: record.context,
            }
        );

        this.env.services.action.doAction(action);
    }
}

ActionBarcodeField.template = xml``;
ActionBarcodeField.props = {...standardFieldProps};

export const actionBarcodeField = {
    component: ActionBarcodeField,
};

registry.category("fields").add("action_barcode_handler", actionBarcodeField);
