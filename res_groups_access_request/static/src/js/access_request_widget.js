odoo.define(
    "res_groups_access_request.permission_request_launcher",
    function (require) {
        "use strict";

        var SystrayMenu = require("web.SystrayMenu");
        var Widget = require("web.Widget");
        var LauncherMenu = Widget.extend({
            template: "permission_request_launcher.view.Menu",
            events: {
                click: "on_click_request_permission",
            },

            on_click_request_permission: function (event) {
                event.preventDefault();
                var context = {search_default_my_requests: 1};
                return this.do_action({
                    view_id:
                        "res_groups_access_request.view_res_groups_access_request_tree",
                    type: "ir.actions.act_window",
                    name: "Request Access",
                    res_model: "res.groups.access.request",
                    views: [
                        [false, "list"],
                        [false, "form"],
                    ],
                    domain: "[('user_id', '=', uid)]",
                    target: "current",
                    context: context,
                });
            },
        });

        SystrayMenu.Items.push(LauncherMenu);
        return {
            LauncherMenu: LauncherMenu,
        };
    }
);
