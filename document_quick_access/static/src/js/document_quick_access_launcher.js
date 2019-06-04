odoo.define('document_quick_access.document_quick_access_launcher', function (require) {
    "use strict";

    var SystrayMenu = require('web.SystrayMenu');
    var Widget = require('web.Widget');
    var LauncherMenu = Widget.extend({
        template:'document_quick_access_launcher.view.Menu',
        events: {
            "click": "on_click_find_document",
        },

        on_click_find_document: function () {
            var context = {};
            context.default_model = 'document.quick.access.rule';
            context.default_method ='read_code_action';
            return this.do_action({
                type: 'ir.actions.act_window',
                name: 'Search QR',
                res_model:  'barcode.action',
                views: [[false, 'form']],
                target: 'new',
                context:context,
            });
        },
    });

    SystrayMenu.Items.push(LauncherMenu);
    return {
        LauncherMenu: LauncherMenu,
    };
});
