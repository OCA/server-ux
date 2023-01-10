odoo.define("easy_switch_user.switch_user_tour", function (require) {
    "use strict";

    const tour = require("web_tour.tour");

    tour.register(
        "easy_switch_user.test_switch_user",
        {
            test: true,
        },
        [
            {
                content: "Check admin user name",
                trigger: "span.oe_topbar_name:contains(Mitchell Admin)",
            },
            {
                content: "Click on Switch User button",
                trigger: "button[name=action_switch_user]",
            },
            {
                content: "Check demo user name",
                trigger: "span.oe_topbar_name:contains(Marc Demo)",
            },
        ]
    );
    return {};
});
