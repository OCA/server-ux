/** @odoo-module */
/* Copyright 2021 Tecnativa - David Vidal
   License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
*/
import {FormController} from "@web/views/form/form_controller";
import {ListController} from "@web/views/list/list_controller";
import {patch} from "@web/core/utils/patch";
import {user} from "@web/core/user";

const GROUP_DUPLICATE = "base_duplicate_security_group.group_duplicate_records";

/**
 * Disable duplicate action for users without permission in both Form and List views.
 * If the user has the permission, the internal logic rules will apply.
 **/
async function disableDuplicate(controller) {
    const hasGroup = await user.hasGroup(GROUP_DUPLICATE);
    if (!hasGroup && controller.archInfo.activeActions) {
        controller.archInfo.activeActions.duplicate = false;
    }
}

// Patch FormController - duplicate button in form view
patch(FormController.prototype, {
    async setup() {
        await super.setup(...arguments);
        await disableDuplicate(this);
    },
});

// Patch ListController - duplicate action on selected records
patch(ListController.prototype, {
    async setup() {
        await super.setup(...arguments);
        await disableDuplicate(this);
    },
});
