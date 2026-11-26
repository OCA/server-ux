/** @odoo-module **/
/* global QUnit */
/* Copyright 2026 Tecnativa - Carlos Lopez
 * License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl). */
import {
    domainFromTreeDateRange,
    restoreDateRangeOperators,
    treeFromDomainDateRange,
} from "@date_range/js/condition_tree.esm";

const DATE_RANGES = [
    {
        id: 1,
        name: "2020",
        date_start: "2020-01-01",
        date_end: "2020-12-31",
        type_id: [7, "Fiscal Year"],
    },
];

const OPTIONS = {
    dateRanges: DATE_RANGES,
    getFieldDef: (path) =>
        path === "date" ? {name: "date", type: "date"} : {name: path, type: "char"},
};

QUnit.module("date_range.condition_tree", {});

QUnit.test("domain matching a date range becomes a daterange condition", (assert) => {
    const domain = `["&", ("date", "<=", "2020-12-31"), ("date", ">=", "2020-01-01")]`;
    const tree = treeFromDomainDateRange(domain, OPTIONS);
    assert.strictEqual(tree.type, "condition");
    assert.strictEqual(tree.operator, "daterange_7");
    assert.deepEqual(tree.value, ["2020-12-31", "2020-01-01"]);
    assert.strictEqual(domainFromTreeDateRange(tree), domain);
});

QUnit.test("domain not matching any date range is kept as it is", (assert) => {
    const domain = `["&", ("date", "<=", "2020-06-30"), ("date", ">=", "2020-01-01")]`;
    const tree = treeFromDomainDateRange(domain, OPTIONS);
    assert.strictEqual(tree.type, "connector");
    assert.deepEqual(
        tree.children.map((c) => c.operator),
        ["<=", ">="]
    );
    assert.strictEqual(domainFromTreeDateRange(tree), domain);
});

QUnit.test(
    "generic daterange operator is restored from the previous tree",
    (assert) => {
        const domain = `["&", ("date", "<=", "2020-12-31"), ("date", ">=", "2020-01-01")]`;
        const previousTree = {
            ...treeFromDomainDateRange(domain, OPTIONS),
            operator: "daterange",
        };
        const tree = treeFromDomainDateRange(domain, OPTIONS);
        restoreDateRangeOperators(tree, previousTree);
        assert.strictEqual(tree.operator, "daterange");
    }
);
