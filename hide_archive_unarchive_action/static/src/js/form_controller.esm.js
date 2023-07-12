/** @odoo-module **/

import {patch} from "@web/core/utils/patch";
import {FormController} from "@web/views/form/form_controller";

patch(FormController.prototype, "hide_archive_unarchive_action.FormController", {
    setup() {
        this._super();
        this.archiveEnabled = this.archiveEnabled && this.canEdit;
    },
});
