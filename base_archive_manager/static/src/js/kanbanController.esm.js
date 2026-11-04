/**
 * Copyright 2026 CIT Services
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
 */

import {KanbanCompiler} from "@web/views/kanban/kanban_compiler";
import {KanbanController} from "@web/views/kanban/kanban_controller";
import {KanbanHeader} from "@web/views/kanban/kanban_header";
import {KanbanRecord} from "@web/views/kanban/kanban_record";
import {patch} from "@web/core/utils/patch";
import {useSubEnv} from "@odoo/owl";

patch(KanbanController.prototype, {
    setup() {
        super.setup(...arguments);
        const xmlDoc = this.props.archInfo.xmlDoc;
        const canArchive = xmlDoc ? xmlDoc.getAttribute("archive") !== "0" : true;
        const canUnarchive = xmlDoc ? xmlDoc.getAttribute("unarchive") !== "0" : true;
        useSubEnv({
            archivePermissions: {archive: canArchive, unarchive: canUnarchive},
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
