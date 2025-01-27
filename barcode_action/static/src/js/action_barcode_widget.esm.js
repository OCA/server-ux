import {registry} from "@web/core/registry";
import {standardFieldProps} from "@web/views/fields/standard_field_props";
import {useBus, useService} from "@web/core/utils/hooks";
import { rpc } from "@web/core/network/rpc";

import {Component, xml} from "@odoo/owl";

export class ActionBarcodeField extends Component {
    setup() {
        const barcode = useService("barcode");
        useBus(barcode.bus, "barcode_scanned", this.onBarcodeScanned);
    }
    onBarcodeScanned(event) {
        const {barcode} = event.detail;
        var self = this;
        var record = this.props.record;
        rpc(`/web/dataset/call_kw/${record.data.model}/${record.data.method}`, {
            model: record.data.model,
            method: record.data.method,
            args: [[record.data.res_id], barcode],
            kwargs: {},
        }).then(function (action) {
            self.env.services.action.doAction(action);
        });
    }
}

ActionBarcodeField.template = xml``;
ActionBarcodeField.props = {...standardFieldProps};

export const actionBarcodeField = {
    component: ActionBarcodeField,
};

registry.category("fields").add("action_barcode_handler", actionBarcodeField);
