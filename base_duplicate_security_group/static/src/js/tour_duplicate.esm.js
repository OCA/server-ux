/** @odoo-module */
/* Copyright 2021 Tecnativa - David Vidal
   License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
*/
import {registry} from "@web/core/registry";

const commonSteps = [
    {
        trigger: ".o_navbar_apps_menu > button.dropdown-toggle",
    },
    {
        content: "Open the settings menu",
        trigger: '[data-menu-xmlid="base.menu_administration"]',
    },
    {
        content: "Open the Users and Companies menu",
        trigger: '.dropdown-toggle[data-menu-xmlid="base.menu_users"]',
    },
    {
        content: "Open the users menu option",
        trigger: '.dropdown-item[data-menu-xmlid="base.menu_action_res_users"]',
    },
    {
        content: "Choose a user",
        trigger: ".o_data_cell:contains('Demo')",
    },
    {
        content: "Pull the actions dropdown",
        trigger: "button.dropdown-toggle:contains('Action')",
    },
];

registry.category("web_tour.tours").add("button_duplicate_ok", {
    test: true,
    url: "/web",
    steps: () => [
        ...commonSteps,
        {
            content: "We can duplicate",
            trigger: "a[role='menuitemcheckbox']:contains('Duplicate')",
        },
    ],
});

registry.category("web_tour.tours").add("button_duplicate_ko", {
    test: true,
    url: "/web",
    steps: () => [
        ...commonSteps,
        {
            trigger:
                ".btn-group:not(:has(a[role='menuitemcheckbox']:contains('Duplicate')))",
        },
    ],
});
