import {domainFromTreeDateRange, treeFromDomainDateRange} from "./condition_tree.esm";

import {onWillStart, useChildSubEnv} from "@odoo/owl";
import {Domain} from "@web/core/domain";
import {DomainSelector} from "@web/core/domain_selector/domain_selector";
import {useService} from "@web/core/utils/hooks";
import {patch} from "@web/core/utils/patch";

const ARCHIVED_DOMAIN = `[("active", "in", [True, False])]`;

patch(DomainSelector.prototype, {
    setup() {
        super.setup();
        this.orm = useService("orm");
        this.dateRanges = [];
        this.dateRangeTypes = [];
        useChildSubEnv({domain: this});
        onWillStart(async () => {
            this.dateRanges = await this.orm.call("date.range", "search_read", []);
            this.dateRangeTypes = await this.orm.call(
                "date.range.type",
                "search_read",
                []
            );
        });
    },

    async onPropsUpdated(p) {
        // First call the parent method to handle the standard domain processing
        await super.onPropsUpdated.apply(this, arguments);

        // If we have a valid tree, apply our date range enhancements
        if (this.tree) {
            let domain = null;
            try {
                domain = new Domain(p.domain);
                this.tree = treeFromDomainDateRange(domain, {
                    distributeNot: !p.isDebugMode,
                });
            } catch (error) {
                // If there's an error with our custom processing, keep the original tree
                console.warn("Date range domain processing failed:", error);
            }
        }
    },
    getOperatorEditorInfo(fieldDef) {
        const info = super.getOperatorEditorInfo(fieldDef);
        const dateRanges = this.dateRanges;
        const dateRangeTypes = this.dateRangeTypes.filter((dt) => dt.date_ranges_exist);
        patch(info, {
            extractProps({value: [operator]}) {
                const props = super.extractProps.apply(this, arguments);
                const isDateField =
                    fieldDef &&
                    (fieldDef.type === "date" || fieldDef.type === "datetime");
                const hasDateRanges = isDateField && dateRanges.length;
                const hasDateRangeTypes = isDateField && dateRangeTypes.length;

                if (hasDateRanges) {
                    if (operator.includes("daterange")) {
                        props.options.pop();
                    }
                    if (operator === "daterange") {
                        props.value = "daterange";
                    }
                    props.options.push(["daterange", "daterange"]);
                }

                if (hasDateRangeTypes) {
                    const selectedDateRange = dateRangeTypes.find(
                        (rangeType) =>
                            rangeType.id === Number(operator.split("daterange_")[1])
                    );

                    if (selectedDateRange) {
                        props.value = operator;
                    }

                    props.options.push(
                        ...dateRangeTypes.map((rangeType) => [
                            `daterange_${rangeType.id}`,
                            `in ${rangeType.name}`,
                        ])
                    );
                }

                return props;
            },
        });
        return info;
    },
    update(tree) {
        const archiveDomain = this.includeArchived ? ARCHIVED_DOMAIN : `[]`;
        const domain = tree
            ? Domain.and([domainFromTreeDateRange(tree), archiveDomain]).toString()
            : archiveDomain;
        this.props.update(domain);
    },
});
