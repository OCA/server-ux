/** @odoo-module **/

import {ListController} from "@web/views/list/list_controller";
import {onWillRender} from "@odoo/owl";
import {patch} from "@web/core/utils/patch";
import {session} from "@web/session";

patch(ListController.prototype, {
    setup() {
        super.setup(...arguments);
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
