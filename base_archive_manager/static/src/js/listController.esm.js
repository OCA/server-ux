/**
 * Copyright 2026 CIT Services
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
 */

import {ListController} from "@web/views/list/list_controller";
import {patch} from "@web/core/utils/patch";

patch(ListController.prototype, {
    getStaticActionMenuItems() {
        const items = super.getStaticActionMenuItems();
        const xmlDoc = this.props.archInfo.xmlDoc;
        const canArchive = xmlDoc ? xmlDoc.getAttribute("archive") !== "0" : true;
        const canUnarchive = xmlDoc ? xmlDoc.getAttribute("unarchive") !== "0" : true;
        if (!canArchive) {
            delete items.archive;
        }
        if (!canUnarchive) {
            delete items.unarchive;
        }
        return items;
    },
});
