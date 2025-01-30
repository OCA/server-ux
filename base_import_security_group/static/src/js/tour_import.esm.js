/** @odoo-module **/
import {registry} from "@web/core/registry";
import {stepUtils} from "@web_tour/tour_service/tour_utils";
registry.category("web_tour.tours").add("button_import_ok", {
    url: "/web",
    test: true,
    steps: () => [
        stepUtils.showAppsMenuItem(),
        {
            trigger: ".o_app[data-menu-xmlid='base.menu_administration']",
            run: "click",
        },
        {
            trigger: ".dropdown-toggle[data-menu-xmlid='base.menu_users']",
            run: "click",
        },
        {
            trigger:
                ".dropdown-item[data-menu-xmlid='base.menu_action_res_company_form']",
            run: "click",
        },
        {
            trigger: ".o_cp_action_menus .dropdown-toggle",
            run: "click",
        },
        {
            trigger: "span.o_import_menu",
            isCheck: true,
        },
    ],
});
registry.category("web_tour.tours").add("button_import_ko", {
    url: "/web",
    test: true,
    steps: () => [
        stepUtils.showAppsMenuItem(),
        {
            trigger: ".o_app[data-menu-xmlid='base.menu_administration']",
            run: "click",
        },
        {
            trigger: ".dropdown-toggle[data-menu-xmlid='base.menu_users']",
            run: "click",
        },
        {
            trigger:
                ".dropdown-item[data-menu-xmlid='base.menu_action_res_company_form']",
            run: "click",
        },
        {
            trigger: ".o_cp_action_menus .dropdown-toggle",
            run: "click",
        },
        {
            trigger: ".dropdown-menu:not(:has(span.o_import_menu))",
            isCheck: true,
        },
    ],
});
