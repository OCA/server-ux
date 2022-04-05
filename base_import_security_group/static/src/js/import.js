odoo.define("web.ListImport", function(require) {
    "use strict";

    var KanbanView = require("web.KanbanView");
    var ListView = require("web.ListView");
    var session = require("web.session");

    var ImportViewMixin = {
        /* eslint-disable no-unused-vars */
        init: function(viewInfo, params) {
            var self = this;
            var res = self._super.apply(self, arguments);
            var base_group = "base_import_security_group.group_import_csv";

            session.user_has_group(base_group).then(function(has_group) {
                var importEnabled = false;
                if (has_group) {
                    importEnabled = true;
                }
                self.controllerParams.importEnabled = importEnabled;
            });
        },
    };

    ListView.include({
        init: function() {
            this._super.apply(this, arguments);
            ImportViewMixin.init.apply(this, arguments);
        },
    });

    KanbanView.include({
        init: function() {
            this._super.apply(this, arguments);
            ImportViewMixin.init.apply(this, arguments);
        },
    });
});
