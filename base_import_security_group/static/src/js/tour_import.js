odoo.define("base_import_security_group.tour", function (require) {
    "use strict";

    var tour = require("web_tour.tour");

    tour.register(
        "button_import_ok",
        {
            test: true,
            url: "/web",
        },
        [
            tour.stepUtils.showAppsMenuItem(),
            {
                id: "settings_menu_click",
                trigger: '.o_app[data-menu-xmlid="base.menu_administration"]',
            },
            {
                id: "settings_menu_users_and_companies",
                trigger: '.dropdown-toggle[data-menu-xmlid="base.menu_users"]',
            },
            {
                id: "settings_menu_companies",
                trigger:
                    '.dropdown-item[data-menu-xmlid="base.menu_action_res_company_form"]',
            },
            {
                id: "favorites_dropdown_click",
                trigger: ".o_favorite_menu > .o_dropdown_toggler_btn",
            },
            {
                trigger: "li.o_import_menu",
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
            tour.stepUtils.showAppsMenuItem(),
            {
                id: "settings_menu_click",
                trigger: '.o_app[data-menu-xmlid="base.menu_administration"]',
            },
            {
                id: "settings_menu_users_and_companies",
                trigger: '.dropdown-toggle[data-menu-xmlid="base.menu_users"]',
            },
            {
                id: "settings_menu_companies",
                trigger:
                    '.dropdown-item[data-menu-xmlid="base.menu_action_res_company_form"]',
            },
            {
                id: "favorites_dropdown_click",
                trigger: ".o_favorite_menu > .o_dropdown_toggler_btn",
            },
            {
                trigger: ".o_dropdown_menu:not(:has(li.o_import_menu))",
            },
        ]
    );
});
