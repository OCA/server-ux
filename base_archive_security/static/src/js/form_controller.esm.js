/** @odoo-module **/

/* Copyright 2023 Camptocamp SA
License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html */

import {FormController} from "@web/views/form/form_controller";
import {onWillStart} from "@odoo/owl";
import {patch} from "@web/core/utils/patch";
import {useService} from "@web/core/utils/hooks";

patch(FormController.prototype, "base_archive_security.FormControllerPatch", {
    setup() {
        this._super();
        this.userService = useService("user");
        onWillStart(async () => {
            this.archiveEnabled =
                this.archiveEnabled &&
                (await this.userService.hasGroup(
                    "base_archive_security.group_can_archive"
                ));
        });
    },
});
