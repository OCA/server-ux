/** @odoo-module */
/* Copyright 2024 Tecnativa - David Vidal
 * Copyright 2024 Tecnativa - Carlos Roca
 * License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl). */
import {registry} from "@web/core/registry";
import {session} from "@web/session";

const {reactive} = owl;

export const announcementService = {
    dependencies: ["orm"],
    async start(env, {orm}) {
        const announcements = reactive({});
        if (session.announcements) {
            Object.assign(announcements, session.announcements);
        } else {
            Object.assign(
                announcements,
                await orm.call("res.users", "get_announcements", [], {
                    context: session.user_context,
                })
            );
        }
        setInterval(async () => {
            Object.assign(
                announcements,
                await orm.call("res.users", "get_announcements", [], {
                    context: session.user_context,
                })
            );
        }, 60000);
        return {
            announcements,
        };
    },
};

registry.category("services").add("announcementService", announcementService);
