/* Copyright 2024 Tecnativa - David Vidal
 * Copyright 2024 Tecnativa - Carlos Roca
 * License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl). */
import {Component, markup, onMounted, useState} from "@odoo/owl";
import {AnnouncementDialog} from "../announcement_dialog/announcement_dialog.esm";
import {Dropdown} from "@web/core/dropdown/dropdown";
import {DropdownItem} from "@web/core/dropdown/dropdown_item";
import {deserializeDateTime} from "@web/core/l10n/dates";
import {registry} from "@web/core/registry";
import {session} from "@web/session";
import {_t} from "@web/core/l10n/translation";
import {useDiscussSystray} from "@mail/utils/common/hooks";
import {user} from "@web/core/user";
import {useService} from "@web/core/utils/hooks";
const {DateTime} = luxon;

export class AnnouncementMenu extends Component {
    setup() {
        this.discussSystray = useDiscussSystray();
        this.orm = useService("orm");
        this.dialogService = useService("dialog");
        const announcements_service = useService("announcementService");
        this.announcements = useState(announcements_service.announcements);
        // When the user logs in we show him his unread announcements
        onMounted(async () => {
            // Let's check if the user just logged in and to decide if we popup the
            // announcements. This delay is hardcoded to 5 minutes, although we could
            // allow to configure it in the future.
            const current_user = await this.orm.call("res.users", "read", [
                user.userId,
                ["login_date"],
            ]);
            const minutes_since_last_login =
                (DateTime.now().toSeconds() -
                    deserializeDateTime(current_user[0]?.login_date).toSeconds()) /
                60;
            const popup_announcement = Boolean(minutes_since_last_login < 5);
            const launchPopUp = () => {
                if (odoo.isReady) {
                    if (popup_announcement && this.announcements.count > 0) {
                        this.openAnnouncement(this.announcements.data[0]);
                    }
                } else {
                    setTimeout(launchPopUp, 500);
                }
            };
            setTimeout(launchPopUp, 500);
        });
    }

    async getDialogAnnouncementProps(announcement) {
        return {
            title: announcement.name,
            body: markup(announcement.content || ""),
            confirm: async () => {
                await this.orm.call(
                    "res.users",
                    "mark_announcement_as_read",
                    [announcement.id],
                    {context: session.user_context}
                );
                this.announcements.data = this.announcements.data.filter(
                    (el) => el.id !== announcement.id
                );
                this.announcements.count--;
                if (this.announcements.count > 0) {
                    this.openAnnouncement(this.announcements.data[0]);
                }
            },
            confirmLabel: _t("Mark as read"),
        };
    }

    // ------------------------------------------------------------
    // Handlers
    // ------------------------------------------------------------

    /**
     * Show announcement popup
     * @private
     * @param {MouseEvent} announcement
     */
    async openAnnouncement(announcement) {
        this.dialogService.add(
            AnnouncementDialog,
            await this.getDialogAnnouncementProps(announcement)
        );
    }
}

AnnouncementMenu.components = {Dropdown, DropdownItem};
AnnouncementMenu.props = [];
AnnouncementMenu.template = "announcement.AnnouncementMenu";

export const systrayAnnouncement = {
    Component: AnnouncementMenu,
};

registry
    .category("systray")
    .add("announcement.announcement_menu", systrayAnnouncement, {sequence: 100});
