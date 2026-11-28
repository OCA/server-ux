import {createDateRangeOperators, domainFromTreeDateRange} from "./condition_tree.esm";

import {providePlugins, usePlugin, useScope} from "@odoo/owl";
import {DateRangePlugin} from "./date_range_plugin.esm";
import {Domain} from "@web/core/domain";
import {DomainSelector} from "@web/core/domain_selector/domain_selector";
import {dateRangeValue} from "./tree_editor.esm";
import {formatValue} from "@web/core/tree_editor/condition_tree";
import {patch} from "@web/core/utils/patch";

const ARCHIVED_DOMAIN = `[("active", "in", [True, False])]`;

function dateRangeKey(path, value) {
    return JSON.stringify([formatValue(path), value]);
}

patch(DomainSelector.prototype, {
    setup() {
        super.setup();
        providePlugins([DateRangePlugin]);
        this.dateRangePlugin = usePlugin(DateRangePlugin);
        // The plugin loads the ranges in parallel with onPropsUpdated
        this.dateRangePluginManager = useScope().pluginManager;
        // Operator picked in the editor for each (path, value), since the
        // domain does not tell "daterange" from "daterange_<type id>"
        this.dateRangeOperators = new Map();
    },

    get dateRanges() {
        return this.dateRangePlugin.dateRanges;
    },

    get dateRangeTypes() {
        return this.dateRangePlugin.dateRangeTypes;
    },

    async onPropsUpdated() {
        await Promise.all([
            super.onPropsUpdated.apply(this, arguments),
            this.dateRangePluginManager.ready,
        ]);
        if (this.tree) {
            this.tree = createDateRangeOperators(this.tree, (path, value) =>
                this.getDateRangeOperator(path, value)
            );
        }
    },

    getDateRangeOperator(path, value) {
        const operator = this.dateRangeOperators.get(dateRangeKey(path, value));
        if (operator) {
            return operator;
        }
        const isRange = this.dateRanges.some((range) =>
            ["date", "datetime"].some(
                (type) =>
                    JSON.stringify(dateRangeValue(range, type)) ===
                    JSON.stringify(value)
            )
        );
        return isRange ? "daterange" : null;
    },

    rememberDateRangeOperators(tree) {
        if (tree.type === "connector") {
            tree.children.forEach((child) => this.rememberDateRangeOperators(child));
        } else if (
            tree.type === "condition" &&
            typeof tree.operator === "string" &&
            tree.operator.includes("daterange")
        ) {
            this.dateRangeOperators.set(
                dateRangeKey(tree.path, tree.value),
                tree.operator
            );
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
        if (tree) {
            this.rememberDateRangeOperators(tree);
        }
        const archiveDomain = this.includeArchived ? ARCHIVED_DOMAIN : `[]`;
        const domain = tree
            ? Domain.and([domainFromTreeDateRange(tree), archiveDomain]).toString()
            : archiveDomain;
        this.props.update(domain);
    },
});
