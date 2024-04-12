/* @odoo-module */
/* Copyright 2024 Tecnativa - Carlos Roca
 * License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl). */
import {AnnouncementMenu} from "@announcement/js/announcement_menu/announcement_menu.esm";
import {patch} from "@web/core/utils/patch";

patch(AnnouncementMenu.prototype, "announcement_dialog_size.AnnouncementMenu", {
    async getDialogAnnouncementProps() {
        const props = await this._super(...arguments);
        const fullsize = await this.orm.call("announcement", "announcement_full_size");
        if (fullsize) {
            props.size = "dialog_full_screen";
        }
        return props;
    },
});
