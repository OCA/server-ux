// Copyright 2021 Tecnativa - David Vidal
// License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
odoo.define("base_duplicate_security_group.tour", function(require) {
    "use strict";

    var tour = require("web_tour.tour");

    tour.register(
        "button_duplicate_ok",
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
                id: "pick_a_user",
                trigger: ".o_data_cell:contains('Demo')",
            },
            {
                id: "pull_dropdown",
                trigger: "button.o_dropdown_toggler_btn:contains('Action')",
            },
            {
                id: "click_duplicate",
                trigger: "a[role='menuitem']:contains('Duplicate')",
            },
        ]
    );
    tour.register(
        "button_duplicate_ko",
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
                id: "pick_a_user",
                trigger: ".o_data_cell:contains('Demo')",
            },
            {
                id: "pull_dropdown",
                trigger: "button.o_dropdown_toggler_btn:contains('Action')",
            },
            {
                trigger:
                    ".btn-group:not(:has(a[role='menuitem']:contains('Duplicate')))",
            },
        ]
    );
});
