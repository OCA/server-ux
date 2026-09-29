/**
 * Copyright 2026 CIT Services
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
 */

import {KanbanCompiler} from "@web/views/kanban/kanban_compiler";
import {KanbanController} from "@web/views/kanban/kanban_controller";
import {KanbanHeader} from "@web/views/kanban/kanban_header";
import {KanbanRecord} from "@web/views/kanban/kanban_record";
import {onWillStart, useSubEnv} from "@odoo/owl";
import {patch} from "@web/core/utils/patch";
import {archiveAccessCache} from "@base_archive_manager/js/archiveAccess.esm";

patch(KanbanController.prototype, {
    setup() {
        super.setup(...arguments);
        this.archivePermissions = {archive: false, unarchive: false};
        useSubEnv({archivePermissions: this.archivePermissions});

        onWillStart(async () => {
            const access = await archiveAccessCache.read(this.props.resModel);
            this.archivePermissions.archive = access.can_archive;
            this.archivePermissions.unarchive = access.can_unarchive;
        });
    },
});

patch(KanbanRecord.prototype, {
    createWidget(props) {
        super.createWidget(props);
        this.dataState.widget.hasArchiveAccess = this.env.archivePermissions
            ? this.env.archivePermissions.archive
            : true;
        this.dataState.widget.hasUnarchiveAccess = this.env.archivePermissions
            ? this.env.archivePermissions.unarchive
            : true;
    },
});

patch(KanbanHeader.prototype, {
    canArchiveGroup() {
        const canArchive = super.canArchiveGroup();
        return (
            canArchive &&
            (this.env.archivePermissions ? this.env.archivePermissions.archive : true)
        );
    },
});

patch(KanbanCompiler.prototype, {
    compileButton(el, params) {
        const type = el.getAttribute("type");
        if (type === "archive") {
            const existingIf = el.getAttribute("t-if");
            el.setAttribute(
                "t-if",
                existingIf
                    ? `(${existingIf}) and widget.hasArchiveAccess`
                    : "widget.hasArchiveAccess"
            );
        }
        if (type === "unarchive") {
            const existingIf = el.getAttribute("t-if");
            el.setAttribute(
                "t-if",
                existingIf
                    ? `(${existingIf}) and widget.hasUnarchiveAccess`
                    : "widget.hasUnarchiveAccess"
            );
        }
        return super.compileButton(el, params);
    },
});
