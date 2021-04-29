odoo.define("base_import_security_group.tour", function(require) {
    "use strict";

    var tour = require("web_tour.tour");

    tour.register(
        "button_import_ok",
        {
            test: true,
            url: "/web",
        },
        [
            tour.STEPS.SHOW_APPS_MENU_ITEM,
            {
                id: "settings_menu_click",
                trigger: '.o_app[data-menu-xmlid="base.menu_administration"]',
            },
            {
                id: "settings_menu_users_and_co",
                trigger: '.dropdown-toggle[data-menu-xmlid="base.menu_users"]',
            },
            {
                id: "settings_menu_users",
                trigger: '.dropdown-item[data-menu-xmlid="base.menu_action_res_users"]',
            },
            {
                trigger: ".o_button_import",
            },
        ]
    );
    tour.register(
        "button_import_ko",
        {
            test: true,
            url: "/web",
        },
        [
            tour.STEPS.SHOW_APPS_MENU_ITEM,
            {
                id: "settings_menu_click",
                trigger: '.o_app[data-menu-xmlid="base.menu_administration"]',
            },
            {
                id: "settings_menu_users_and_co",
                trigger: '.dropdown-toggle[data-menu-xmlid="base.menu_users"]',
            },
            {
                id: "settings_menu_users",
                trigger: '.dropdown-item[data-menu-xmlid="base.menu_action_res_users"]',
            },
            {
                trigger: ".o_list_buttons:not(:has(.o_button_import))",
            },
        ]
    );
});
