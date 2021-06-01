/*
 * Copyright 2021 Stefan Rijnhart <stefan@opener.amsterdam>
 * Copyright 2021 Chandresh Thakkar OSI <cthakkar@opensourceintegrators.com>
 * Copyright 2019 Iryna Vushnevska <i.vyshnevska@mobilunity.com>
 * Copyright 2017 Antonio Esposito <a.esposito@onestein.nl>
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
 *
 * Patch the method on the ImportMenu class that determines whether the
 * import button under Favorites will be displayed to return false if the
 * user does not belong to this module's access group.
 */
odoo.define("base_import_security_group.group_import", function (require) {
    "use strict";

    const ImportMenu = require("base_import.ImportMenu");
    const shouldBeDisplayed_orig = ImportMenu.shouldBeDisplayed;

    ImportMenu.shouldBeDisplayed = function (env) {
        return (
            shouldBeDisplayed_orig(env) &&
            env.session.base_import_security_group__allow_import === 1
        );
    };
});
