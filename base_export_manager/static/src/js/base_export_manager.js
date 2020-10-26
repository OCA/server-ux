/* Copyright 2019 brain-tec AG (Brig, Switzerland, http://www.braintec-group.com)
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
 */

odoo.define("base_export_manager.base_export_manager", function (require) {
    "use strict";

    const core = require("web.core");
    const Sidebar = require("web.Sidebar");
    const session = require("web.session");

    const _t = core._t;

    Sidebar.include({
        /**
         * Reject "export" item if the current user has not 'export perm' in
         * the active model
         *
         * @override
         */
        _addItems: function (sectionCode, items) {
            let _items = items;
            const is_export_enabled =
                session.export_models.indexOf(this.env.model) !== -1;
            if (
                !session.is_system &&
                sectionCode === "other" &&
                items.length &&
                !is_export_enabled
            ) {
                _items = _.reject(_items, {label: _t("Export")});
            }
            this._super(sectionCode, _items);
        },
    });
});
