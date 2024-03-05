/** @odoo-module */

import { registry } from "@web/core/registry";
import { session } from "@web/session";
// import { memoize } from "@web/core/utils/functions";

const { reactive } = owl;

export const announcementService = {
    dependencies: ["rpc", "orm"],
    async start(env, { rpc, orm }) {
        const announcements = reactive({});

        if (session.announcements) {
            Object.assign(announcements, session.announcements);
        } else {
            Object.assign(announcements, await orm.call("res.users", "get_announcements", [], {context: session.user_context}));
        }

        setInterval(async () => {
            Object.assign(announcements, await orm.call("res.users", "get_announcements", [], {context: session.user_context}));
        }, 60000);

        // async function loadCustomers() {
        //     return await orm.searchRead("res.partner", [], ["display_name"]);
        // }

        return {
            announcements,
        };
    },
};

registry.category("services").add("announcementService", announcementService);
