import {
    deserializeDate,
    deserializeDateTime,
    serializeDate,
    serializeDateTime,
} from "@web/core/l10n/dates";
import {DateRangePlugin} from "./date_range_plugin.esm";
import {Select} from "@web/core/tree_editor/tree_editor_components";
import {TreeEditor} from "@web/core/tree_editor/tree_editor";
import {patch} from "@web/core/utils/patch";
import {useScope} from "@odoo/owl";

function toDateTime(date, type, end) {
    if (type === "date") {
        return date;
    }
    let jsDate = deserializeDate(date);
    if (end) {
        jsDate = luxon.DateTime.fromObject({
            ...jsDate.c,
            hour: 23,
            minute: 59,
            second: 59,
        });
    }
    return serializeDateTime(jsDate);
}

function fromDateTime(date, type) {
    if (type === "date") {
        return date;
    }
    return serializeDate(deserializeDateTime(date));
}

/**
 * Domain value of a date range, as written by the date range operators:
 * the end bound first, so that the core does not read the pair as a between.
 */
export function dateRangeValue(range, type) {
    return [toDateTime(range.date_end, type, true), toDateTime(range.date_start, type)];
}

function dateRangeTypeId(operator) {
    return Number(operator.split("daterange_")[1]);
}

patch(TreeEditor.prototype, {
    setup() {
        super.setup();
        // Provided by the DomainSelector; absent when the TreeEditor is used alone
        this.dateRangePlugin = useScope().pluginManager.getPlugin(DateRangePlugin);
    },
    getValueEditorInfo(node) {
        const fieldDef = this.getFieldDef(node.path);
        const info = super.getValueEditorInfo.apply(this, arguments);
        if (
            fieldDef &&
            (fieldDef.type === "date" || fieldDef.type === "datetime") &&
            node.operator.includes("daterange")
        ) {
            info.component = Select;
        }
        if (this.dateRangePlugin) {
            let dateRanges = this.dateRangePlugin.dateRanges;
            const typeId = dateRangeTypeId(node.operator);
            if (typeId) {
                dateRanges = dateRanges.filter((range) => range.type_id[0] === typeId);
            }
            patch(info, {
                extractProps({value, update}) {
                    const props = super.extractProps.apply(this, arguments);
                    if (
                        fieldDef &&
                        (fieldDef.type === "date" || fieldDef.type === "datetime") &&
                        node.operator.includes("daterange")
                    ) {
                        let selected = dateRanges.find(
                            (range) =>
                                range.date_start ===
                                    fromDateTime(value[1], fieldDef.type) &&
                                range.date_end === fromDateTime(value[0], fieldDef.type)
                        );
                        if (!selected) {
                            selected = dateRanges[0];
                            update(dateRangeValue(selected, fieldDef.type));
                        }

                        return {
                            options: dateRanges.map((dt) => [dt.id, dt.name]),
                            update: (v) => {
                                const range = dateRanges.find((r) => r.id === v);
                                update(dateRangeValue(range, fieldDef.type));
                            },
                            value: selected.id,
                        };
                    }

                    return props;
                },
                isSupported(value) {
                    if (node.operator.includes("daterange")) {
                        return Array.isArray(value) && value.length === 2;
                    }
                    return super.isSupported.apply(this, arguments);
                },
            });
        }
        return info;
    },

    getOperatorEditorInfo(node) {
        const info = super.getOperatorEditorInfo(node);
        patch(info, {
            isSupported([operator]) {
                if (node.operator.includes("daterange")) {
                    return (
                        typeof operator === "string" && operator.includes("daterange")
                    );
                }
                return super.isSupported.apply(this, arguments);
            },
        });
        return info;
    },

    _updateLeafOperator(node, operator, negate) {
        if (
            !this.dateRangePlugin ||
            typeof operator !== "string" ||
            !operator.includes("daterange")
        ) {
            return super._updateLeafOperator(...arguments);
        }
        const allRanges = this.dateRangePlugin.dateRanges;
        const typeId = dateRangeTypeId(operator);
        const dateRanges = allRanges.filter((range) => range.type_id[0] === typeId);
        node.negate = negate;
        node.operator = operator;
        node.value = dateRangeValue(
            (dateRanges.length ? dateRanges : allRanges)[0],
            this.getFieldDef(node.path).type
        );
    },
});
