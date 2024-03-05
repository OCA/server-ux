/** @odoo-module **/
import {AnnouncementMenuContainer} from "./announcement_menu_container/announcement_menu_container";
import {registry} from "@web/core/registry";

const systrayRegistry = registry.category("systray");
const serviceRegistry = registry.category("services");

export const systrayService = {
    start() {
        systrayRegistry.add(
            "announcement.AnnouncementMenu",
            {Component: AnnouncementMenuContainer},
            {sequence: 100}
        );
    },
};

serviceRegistry.add("announcement_systray_service", systrayService);
