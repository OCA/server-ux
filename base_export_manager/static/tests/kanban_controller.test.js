import {beforeEach, expect, test} from "@odoo/hoot";
import {
    contains,
    defineModels,
    fields,
    models,
    mountView,
    onRpc,
    patchWithCleanup,
} from "@web/../tests/web_test_helpers";
import {keyDown, keyUp} from "@odoo/hoot-dom";
import {animationFrame} from "@odoo/hoot-mock";
import {session} from "@web/session";
import {user} from "@web/core/user";

class Partner extends models.Model {
    name = fields.Char();

    _records = [
        {id: 1, name: "first"},
        {id: 2, name: "second"},
    ];
}

defineModels([Partner]);

beforeEach(() => {
    onRpc("has_group", ({args}) => args[1] === "base.group_allow_export");
});

async function openKanbanActionMenu() {
    await mountView({
        type: "kanban",
        resModel: "partner",
        arch: `
            <kanban>
                <templates>
                    <t t-name="card">
                        <field name="name"/>
                    </t>
                </templates>
            </kanban>`,
        loadActionMenus: true,
    });
    await keyDown("alt");
    await animationFrame();
    await contains(".o_kanban_record:nth-of-type(1)").click();
    await keyUp("alt");
    await contains(".o_cp_action_menus button").click();
}

test("kanban hides Export for a model without export access", async () => {
    patchWithCleanup(session, {export_models: []});
    patchWithCleanup(user, {isSystem: false});
    await openKanbanActionMenu();
    expect(".o-dropdown--menu .o_menu_item:contains(Export)").toHaveCount(0);
});

test("kanban shows Export for a model with export access", async () => {
    patchWithCleanup(session, {export_models: ["partner"]});
    patchWithCleanup(user, {isSystem: false});
    await openKanbanActionMenu();
    expect(".o-dropdown--menu .o_menu_item:contains(Export)").toHaveCount(1);
});

test("kanban shows Export to a system user regardless of export access", async () => {
    patchWithCleanup(session, {export_models: []});
    patchWithCleanup(user, {isSystem: true});
    await openKanbanActionMenu();
    expect(".o-dropdown--menu .o_menu_item:contains(Export)").toHaveCount(1);
});
