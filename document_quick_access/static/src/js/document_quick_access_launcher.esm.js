/* @odoo-module */

import {Component} from "@odoo/owl";
import {registry} from "@web/core/registry";
import {useService} from "@web/core/utils/hooks";

export class DocumentQuickAccessSystrayItem extends Component {
    static template = "document_quick_access_launcher.view.Menu";
    setup() {
        this.action = useService("action");
    }
    onClick(ev) {
        ev.preventDefault();
        ev.stopPropagation();
        var context = {};
        context.default_model = "document.quick.access.rule";
        context.default_method = "read_code_action";
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "Search QR",
            res_model: "barcode.action",
            views: [[false, "form"]],
            target: "new",
            context: context,
        });
    }
}
registry
    .category("systray")
    .add("document_quick_access_launcher", {Component: DocumentQuickAccessSystrayItem});
