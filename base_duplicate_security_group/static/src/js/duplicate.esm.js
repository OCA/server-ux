/** @odoo-module */
/* Copyright 2021 Tecnativa - David Vidal
   License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
*/
import {FormController} from "@web/views/form/form_controller";
import {patch} from "@web/core/utils/patch";
import {user} from "@web/core/user";

/**
 * Patch FormController to disable duplicate action for users without permission.
 * If the user has the permission, the internal logic rules will apply.
 **/
patch(FormController.prototype, {
    async setup() {
        await super.setup(...arguments);
        const base_group = "base_duplicate_security_group.group_duplicate_records";
        const hasGroup = await user.hasGroup(base_group);
        if (!hasGroup && this.archInfo.activeActions) {
            this.archInfo.activeActions.duplicate = false;
        }
    },
});
