/** @odoo-module **/

import {patch} from "@web/core/utils/patch";
import {ListController} from "@web/views/list/list_controller";

patch(ListController.prototype, "hide_archive_unarchive_action.ListController", {
    setup() {
        this._super();
        this.archiveEnabled = this.archiveEnabled && this.activeActions.edit;
    },
});
