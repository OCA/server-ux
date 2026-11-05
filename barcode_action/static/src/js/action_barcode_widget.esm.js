import {Component, useProps, xml} from "@odoo/owl";
import {useBus, useService} from "@web/core/utils/hooks";
import {registry} from "@web/core/registry";
import {standardFieldProps} from "@web/views/fields/standard_field_props";

export const actionBarcodeFieldProps = {
    ...standardFieldProps,
};

export class ActionBarcodeField extends Component {
    static template = xml``;
    props = useProps(actionBarcodeFieldProps);

    setup() {
        const barcode = useService("barcode");
        this.orm = useService("orm");
        // Owl 3 calls the handler with the bus as `this`, so it is bound
        // explicitly to the component here.
        useBus(barcode.bus, "barcode_scanned", (event) => this.onBarcodeScanned(event));
    }

    async onBarcodeScanned(event) {
        const {barcode} = event.detail;
        const record = this.props.record;

        // `res_id` is 0 when the launcher targets no particular record, and
        // 20.0 rejects `browse([0])` ("Invalid falsy real id"), so an empty
        // recordset is passed instead.
        const resIds = record.data.res_id ? [record.data.res_id] : [];
        const action = await this.orm.call(
            record.data.model,
            record.data.method,
            [resIds, barcode],
            {
                context: record.context,
            }
        );

        this.env.services.action.doAction(action);
    }
}

export const actionBarcodeField = {
    component: ActionBarcodeField,
};

registry.category("fields").add("action_barcode_handler", actionBarcodeField);
