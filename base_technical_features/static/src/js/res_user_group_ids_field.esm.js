// Copyright 2026 Tecnativa - Andrii Kompaniiets
// License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
import {onWillStart, toRaw} from "@odoo/owl";
import {registry} from "@web/core/registry";
import {patch} from "@web/core/utils/patch";
import {user} from "@web/core/user";
import {parseXML} from "@web/core/utils/xml";
import {FormArchParser} from "@web/views/form/form_arch_parser";

const ResUserGroupIdsField = registry
    .category("fields")
    .get("res_user_group_ids").component;

patch(ResUserGroupIdsField.prototype, {
    setup() {
        super.setup();
        onWillStart(async () => {
            // If debug mode is enabled, there's no need to enable Technical Features.
            if (
                odoo.debug ||
                !(await user.hasGroup(
                    "base_technical_features.group_technical_features"
                ))
            ) {
                return;
            }
            const {categories} = toRaw(this.props.record.data.view_group_hierarchy);
            const models = {main: {fields: this._fields}};
            // Copied from ResUserGroupIdsField.setup() (Odoo 19.0) to include the
            // extra rights groups without debug mode. Keep in sync with core:
            // https://github.com/odoo/odoo/blob/b7de5c9cc43057dcd2741871087ab5953cd134ee/addons/web/static/src/webclient/res_user_group_ids_field/res_user_group_ids_field.js#L97-L102
            const arch = `
                <t>
                    <group>
                        ${categories
                            .map((category) => this.getCategoryArch(category))
                            .join("")}
                    </group>
                    ${this.getExtraGroupsArch()}
                </t>`;
            this.archInfo = new FormArchParser().parse(parseXML(arch), models, "main");
        });
    },
});
