import {Component} from "@odoo/owl";
import {_t} from "@web/core/l10n/translation";
import {registry} from "@web/core/registry";
import {useService} from "@web/core/utils/hooks";

export class BarcodeActionSystrayItem extends Component {
    static template = "barcode_action.SystrayItem";
    static props = {};

    setup() {
        this.action = useService("action");
    }

    onClick(ev) {
        ev.preventDefault();
        ev.stopPropagation();
        this.action.doAction({
            type: "ir.actions.act_window",
            name: _t("Find Partner"),
            res_model: "barcode.action",
            views: [[false, "form"]],
            target: "new",
            context: {
                default_model: "res.partner",
                default_method: "find_res_partner_by_ref_using_barcode",
            },
        });
    }
}

registry
    .category("systray")
    .add("barcode_action.SystrayItem", {Component: BarcodeActionSystrayItem});
