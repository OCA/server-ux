/* Copyright 2019 brain-tec AG (Brig, Switzerland, http://www.braintec-group.com)
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
 */

odoo.define("base_export_manager.base_export_manager", function (require) {
    "use strict";

    const ListController = require("web.ListController");
    const session = require("web.session");

    ListController.include({
        /**
         * Reject "export" item if the current user has not 'export perm' in
         * the active model
         * @private
         * @returns {Promise}
         */
        _getActionMenuItems: function () {
            const is_export_enabled =
                session.export_models.indexOf(this.modelName) !== -1;
            if (!session.is_system && !is_export_enabled) {
                this.isExportEnable = false;
            }
            return this._super(...arguments);
        },
    });
});
