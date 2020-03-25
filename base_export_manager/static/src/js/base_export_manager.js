/* Copyright 2019 brain-tec AG (Brig, Switzerland, http://www.braintec-group.com)
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
 */

odoo.define("base_export_manager.base_export_manager", function(require) {
    "use strict";

    var core = require("web.core");
    var Sidebar = require("web.Sidebar");
    var session = require("web.session");
    var _t = core._t;

    Sidebar.include({
        _addItems: function(sectionCode, items) {
            var _items = items;
            var render_export_enalble = jQuery.inArray(
                this.env.model,
                session.export_models
            );
            if (
                !session.is_superuser &&
                sectionCode === "other" &&
                items.length &&
                render_export_enalble < 0
            ) {
                _items = _.reject(_items, {label: _t("Export")});
            }
            this._super(sectionCode, _items);
        },
    });
});
