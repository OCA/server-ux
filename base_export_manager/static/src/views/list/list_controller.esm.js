/** @odoo-module **/

import {ListController} from "@web/views/list/list_controller";
const {onWillRender} = owl;
import {patch} from "@web/core/utils/patch";
import {session} from "@web/session";

patch(ListController.prototype, "base_export_manager", {
    setup() {
        this._super(...arguments);
        onWillRender(async () => {
            if (this.isExportEnable) {
                const is_export_enabled =
                    session.export_models.indexOf(this.model.root.resModel) !== -1;
                if (!session.is_system && !is_export_enabled) {
                    this.isExportEnable = false;
                }
            }
        });
    },
});
