// Copyright 2021 Tecnativa - David Vidal
// License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
odoo.define("base_duplicate_security_group.DuplicateSecurity", function(require) {
    "use strict";

    const FormView = require("web.FormView");
    const session = require("web.session");

    /**
     * Use this mixin if any view relied in this controller value as well to let
     * the user duplicate records.
     * If the user has the permission, the internal logic rules will apply.
     **/
    const DuplicateViewMixin = {
        init: function() {
            this._super.apply(this, arguments);
            const base_group = "base_duplicate_security_group.group_duplicate_records";
            session.user_has_group(base_group).then(result => {
                if (!result) {
                    this.controllerParams.activeActions.duplicate = false;
                }
            });
        },
    };

    FormView.include(DuplicateViewMixin);

    return DuplicateViewMixin;
});
