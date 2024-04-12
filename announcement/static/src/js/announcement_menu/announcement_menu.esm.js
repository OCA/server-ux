/* @odoo-module */
/* Copyright 2024 Tecnativa - David Vidal
 * Copyright 2024 Tecnativa - Carlos Roca
 * License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl). */
import {Component, markup, onMounted, useState} from "@odoo/owl";
import {_lt} from "@web/core/l10n/translation";
import {Dropdown} from "@web/core/dropdown/dropdown";
import {DropdownItem} from "@web/core/dropdown/dropdown_item";
import {session} from "@web/session";
import {registry} from "@web/core/registry";
import {useService} from "@web/core/utils/hooks";
import {AnnouncementDialog} from "../announcement_dialog/announcement_dialog.esm";

export class AnnouncementMenu extends Component {
    setup() {
        this.orm = useService("orm");
        this.dialogService = useService("dialog");
        const announcements_service = useService("announcementService");
        this.announcements = useState(announcements_service.announcements);
        this.announcementMenuView = useState({isOpen: false});
        // When the user logs in we show him his unread announcements
        onMounted(async () => {
            document.addEventListener(
                "click",
                this._onClickCaptureGlobal.bind(this),
                true
            );
            // Let's check if the user just logged in and to decide if we popup the
            // announcements. This delay is hardcoded to 5 minutes, although we could
            // allow to configure it in the future.
            const user = await this.orm.call("res.users", "read", [
                session.uid,
                ["login_date"],
            ]);
            const login_date = !_.isEmpty(user) && user[0].login_date;
            const minutes_since_last_login =
                (moment.utc(new Date()).valueOf() - moment.utc(login_date).valueOf()) /
                1000 /
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
            confirmLabel: _lt("Mark as read"),
        };
    }

    // ------------------------------------------------------------
    // Handlers
    // ------------------------------------------------------------

    /**
     * Toggle dropdown when clicking it
     * @private
     */
    onClickDropdownToggle() {
        this.announcementMenuView.isOpen = !this.announcementMenuView.isOpen;
    }

    /**
     * Hide dropdown when clicking outside
     * @private
     * @param {MouseEvent} ev
     */
    _onClickCaptureGlobal(ev) {
        if (this.__owl__.refs.root.contains(ev.target)) {
            return;
        }
        this.announcementMenuView.isOpen = false;
    }

    /**
     * Show announcement popup
     * @private
     * @param {MouseEvent} event
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
