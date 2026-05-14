import {useBus, useService} from "@web/core/utils/hooks";
import {Component} from "@odoo/owl";
import {_t} from "@web/core/l10n/translation";
import {registry} from "@web/core/registry";
import {standardFieldProps} from "@web/views/fields/standard_field_props";

export class ActionBarcodeField extends Component {
    static template = "barcode_action.ActionBarcodeField";
    static props = {...standardFieldProps};

    setup() {
        const barcode = useService("barcode");
        this.action = useService("action");
        this.notification = useService("notification");
        this.orm = useService("orm");
        useBus(barcode.bus, "barcode_scanned", this.onBarcodeScanned);
    }

    async onBarcodeScanned(event) {
        const {barcode} = event.detail;
        const record = this.props.record;

        let action = null;
        try {
            action = await this.orm.call(
                record.data.model,
                record.data.method,
                [[record.data.res_id], barcode],
                {
                    context: record.context,
                }
            );
        } catch (error) {
            this.notification.add(
                error.data?.message || error.message || _t("Unknown error"),
                {
                    title: _t("Barcode action failed"),
                    type: "danger",
                }
            );
            return;
        }

        if (action) {
            this.action.doAction(action);
        }
    }
}

export const actionBarcodeField = {
    component: ActionBarcodeField,
};

registry.category("fields").add("action_barcode_handler", actionBarcodeField);
