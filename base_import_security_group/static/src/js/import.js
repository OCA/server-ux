/** @odoo-module **/

import {ImportRecords} from "@base_import/import_records/import_records";
import {registry} from "@web/core/registry";
import {useService} from "@web/core/utils/hooks";
const {Component, onWillStart, useState} = owl;
import {patch} from "@web/core/utils/patch";

patch(ImportRecords.prototype, "base_import_security_group/static/src/js/import.js", {
    setup() {
        this._super();
        this.user = useService("user");
        onWillStart(async () => {
            this.hasImportRecords = await this.user.hasGroup(
                "base_import_security_group.group_import_csv"
            );
        });
    },
});
