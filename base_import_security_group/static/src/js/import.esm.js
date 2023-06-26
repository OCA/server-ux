/** @odoo-module **/

/*
 * Copyright 2023 ACSONE SA/NV
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

import {importRecordsItem} from "@base_import/import_records/import_records";
import {session} from "@web/session";
const isDisplayed_orig = importRecordsItem.isDisplayed;

importRecordsItem.isDisplayed = function (config, isSmall) {
    return (
        isDisplayed_orig(config, isSmall) &&
        session.base_import_security_group__allow_import === 1
    );
};
