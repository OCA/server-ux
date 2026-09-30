import {Component, xml} from "@odoo/owl";
import {
    Country,
    Partner,
    Player,
    Product,
    Stage,
    Team,
    getCurrentOperator,
    getCurrentValue,
    getOperatorOptions,
    getValueOptions,
} from "@web/../tests/core/tree_editor/condition_tree_editor_test_helpers";
import {
    defineModels,
    fields,
    models,
    mountWithCleanup,
} from "@web/../tests/web_test_helpers";
import {expect, test} from "@odoo/hoot";
import {DomainSelector} from "@web/core/domain_selector/domain_selector";

class DateRangeType extends models.Model {
    _name = "date.range.type";

    name = fields.Char();
    date_ranges_exist = fields.Boolean();

    _records = [{id: 1, name: "Fiscal Year", date_ranges_exist: true}];
}

class DateRange extends models.Model {
    _name = "date.range";

    name = fields.Char();
    date_start = fields.Date();
    date_end = fields.Date();
    type_id = fields.Many2one({relation: "date.range.type"});

    _records = [
        {
            id: 1,
            name: "FY 2026",
            date_start: "2026-01-01",
            date_end: "2026-12-31",
            type_id: 1,
        },
    ];
}

defineModels([
    Partner,
    Product,
    Country,
    Stage,
    Team,
    Player,
    DateRange,
    DateRangeType,
]);

async function mountDomainSelector(domain) {
    class Parent extends Component {
        static components = {DomainSelector};
        static template = xml`<DomainSelector t-props="this.domainSelectorProps"/>`;
        setup() {
            this.domainSelectorProps = {
                resModel: "partner",
                readonly: false,
                domain,
                update: (newDomain) => {
                    this.domainSelectorProps.domain = newDomain;
                },
            };
        }
    }
    await mountWithCleanup(Parent);
}

test("date range operators are offered on date fields", async () => {
    await mountDomainSelector(`[("date", "=", "2026-01-01")]`);
    expect(getOperatorOptions()).toInclude("daterange");
    expect(getOperatorOptions()).toInclude("in Fiscal Year");
});

test("a date range domain is shown as a daterange condition", async () => {
    await mountDomainSelector(
        `[("date", "<=", "2026-12-31"), ("date", ">=", "2026-01-01")]`
    );
    expect(getCurrentOperator()).toBe("daterange");
    expect(getValueOptions()).toEqual(["FY 2026"]);
    expect(getCurrentValue()).toBe("FY 2026");
});
