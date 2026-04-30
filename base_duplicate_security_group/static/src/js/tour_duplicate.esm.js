/** @odoo-module */
/* Copyright 2021 Tecnativa - David Vidal
   License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
*/
import {registry} from "@web/core/registry";

const commonSteps = [
    {
        trigger: ".o_navbar_apps_menu > button.dropdown-toggle",
        run: "click",
    },
    {
        content: "Open the settings menu",
        trigger: '[data-menu-xmlid="base.menu_administration"]',
        run: "click",
    },
    {
        content: "Open the Users and Companies menu",
        trigger: '[data-menu-xmlid="base.menu_users"]',
        run: "click",
    },
    {
        content: "Open the users menu option",
        trigger: '[data-menu-xmlid="base.menu_action_res_users"]',
        run: "click",
    },
    {
        content: "Wait for users list",
        trigger: ".o_list_view",
    },
    {
        content: "Choose a user",
        trigger: ".o_data_cell",
        run: "click",
    },
    {
        content: "Wait for form view to load",
        trigger: ".o_form_view",
    },
    {
        content: "Open Action menu",
        trigger: ".o_cp_action_menus button",
        run: "click",
    },
];

registry.category("web_tour.tours").add("button_duplicate_ok", {
    test: true,
    url: "/web",
    steps: () => [
        ...commonSteps,
        {
            content: "We can duplicate",
            trigger:
                ".dropdown-menu .dropdown-item:contains('Duplicate'), " +
                ".dropdown-menu button:contains('Duplicate'), " +
                ".dropdown-menu a:contains('Duplicate')",
            run: "click",
        },
    ],
});

registry.category("web_tour.tours").add("button_duplicate_ko", {
    test: true,
    url: "/web",
    steps: () => [
        ...commonSteps,
        {
            content: "We cannot duplicate",
            trigger:
                ".dropdown-menu:not(:has(.dropdown-item:contains('Duplicate'))):not(:has(button:contains('Duplicate'))):not(:has(a:contains('Duplicate')))",
        },
    ],
});
