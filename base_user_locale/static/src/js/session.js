// Copyright 2019 Brainbean Apps (https://brainbeanapps.com)
// License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
odoo.define('base_user_locale.session', function(require) {
    'use strict';

    var core = require('web.core');
    var Session = require('web.Session');

    var _t = core._t;

    Session.include({
        /**
         * @override
         */
        load_modules: function () {
            var self = this;
            return this._super.apply(this, arguments).then(function () {
                return self.configure_locale();
            });
        },
        /**
         * See https://github.com/odoo/odoo/pull/36532
         */
        configure_locale: function () {
            moment.updateLocale(moment.locale(), {
                week: {
                    // Moment uses index 0 for Sunday but Odoo stores it as 7:
                    dow: (_t.database.parameters.week_start || 0) % 7,
                },
            });
            return Promise.resolve();
        },
    });
});
