/* global QUnit */
odoo.define("web_hide_custom_search.tests", function (require) {
    const CustomFilterItem = require("web.CustomFilterItem");
    const CustomGroupByItem = require("web.CustomGroupByItem");
    const ActionModel = require("web.ActionModel");
    const testUtils = require("web.test_utils");
    const rpc = require("web.rpc");
    const {createComponent} = testUtils;

    function createTestComponent(Component, rpcVisible = true) {
        const originalQuery = rpc.query;
        rpc.query = (params) => {
            if (
                params.model === "ir.model" &&
                params.method === "is_custom_search_visible"
            ) {
                return Promise.resolve(rpcVisible);
            }
            return originalQuery.apply(this, arguments);
        };
        return createComponent(Component, {
            props: {
                fields: [
                    {sortable: true, name: "date", string: "Super Date", type: "date"},
                ],
            },
            env: {
                searchModel: new ActionModel(),
            },
        }).then((cmp) => {
            rpc.query = originalQuery; // Restore after setup
            return cmp;
        });
    }

    QUnit.module("Components", {}, function () {
        QUnit.module("web_hide_custom_search");

        QUnit.test("Custom Filter Visible", async function (assert) {
            assert.expect(1);
            const cgi = await createTestComponent(CustomFilterItem);
            assert.strictEqual(cgi.el.innerText.trim(), "Add Custom Filter");
            cgi.destroy();
        });

        QUnit.test("Custom Filter Invisible", async function (assert) {
            assert.expect(1);
            const cgi = await createTestComponent(CustomFilterItem, false);
            assert.notStrictEqual(cgi.el.innerText.trim(), "Add Custom Filter");
            cgi.destroy();
        });

        QUnit.test("Custom Group By Visible", async function (assert) {
            assert.expect(1);
            const cgi = await createTestComponent(CustomGroupByItem);
            assert.strictEqual(cgi.el.innerText.trim(), "Add Custom Group");
            cgi.destroy();
        });

        QUnit.test("Custom Group By Invisible", async function (assert) {
            assert.expect(1);
            const cgi = await createTestComponent(CustomGroupByItem, false);
            assert.notStrictEqual(cgi.el.innerText.trim(), "Add Custom Group");
            cgi.destroy();
        });
    });
});
