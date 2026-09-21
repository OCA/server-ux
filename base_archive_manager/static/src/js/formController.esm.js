/**
 * Copyright 2026 CIT Services
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
 */

import {archiveAccessCache} from "@base_archive_manager/js/archiveAccess.esm";
import {FormController} from "@web/views/form/form_controller";
import {onWillStart} from "@odoo/owl";
import {patch} from "@web/core/utils/patch";

export const getArchiveAccessPatch = () => ({
    setup() {
        super.setup(...arguments);
        this.hasArchiveAccess = false;
        this.hasUnarchiveAccess = false;

        onWillStart(async () => {
            // Only fetch access rights if the model supports archiving
            const hasActiveField =
                "active" in this.props.fields || "x_active" in this.props.fields;
            if (hasActiveField) {
                const access = await archiveAccessCache.read(this.props.resModel);
                this.hasArchiveAccess = access.can_archive;
                this.hasUnarchiveAccess = access.can_unarchive;
            }
        });
    },

    getStaticActionMenuItems() {
        const menuItems = super.getStaticActionMenuItems(...arguments);

        const applyAccessCheck = (menuItem, hasAccess) => {
            if (!menuItem) return;
            const originalIsAvailable = menuItem.isAvailable;
            menuItem.isAvailable = () => {
                const isAvailable =
                    typeof originalIsAvailable === "function"
                        ? originalIsAvailable()
                        : (originalIsAvailable ?? true);
                return isAvailable && hasAccess;
            };
        };

        applyAccessCheck(menuItems.archive, this.hasArchiveAccess);
        applyAccessCheck(menuItems.unarchive, this.hasUnarchiveAccess);

        return menuItems;
    },
});

patch(FormController.prototype, getArchiveAccessPatch());
