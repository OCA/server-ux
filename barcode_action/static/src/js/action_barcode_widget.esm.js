/** @odoo-module **/

import {registry} from "@web/core/registry";
import {standardFieldProps} from "@web/views/fields/standard_field_props";
import {useBus, useService} from "@web/core/utils/hooks";

const {Component, xml} = owl;

export class ActionBarcodeField extends Component {
    setup() {
        const barcode = useService("barcode");
        this.rpc = useService("rpc");
        useBus(barcode.bus, "barcode_scanned", this.onBarcodeScanned);
    }
    onBarcodeScanned(event) {
        const {barcode} = event.detail;
        var self = this;
        var record = this.props.record;
        this.rpc(`/web/dataset/call_kw/${record.data.model}/${record.data.method}`, {
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

registry.category("fields").add("action_barcode_handler", ActionBarcodeField);
