/** @odoo-module **/
import {patch} from "@web/core/utils/patch";
import {_lt} from "@web/core/l10n/translation";
import {session} from "@web/session";
import {FIELD_OPERATORS, FIELD_TYPES} from "web.searchUtils";
import CustomFilterItem from "web.CustomFilterItem";

patch(CustomFilterItem.prototype, "date_range.CustomFilterItem", {
    /**
     * Ideally we'd want this in setup, but CustomFilterItem does its initialization
     * in the constructor, which can't be patched.
     *
     * Doing it here works just as well.
     *
     * @override
     */
    async willStart() {
        this._super(...arguments);
        this._computeDateRangeOperators();
    },

    async _computeDateRangeOperators() {
        this.OPERATORS = Object.assign({}, FIELD_OPERATORS);
        this.OPERATORS.date = [...FIELD_OPERATORS.date];
        this.OPERATORS.datetime = [...FIELD_OPERATORS.datetime];
        this.date_ranges = {};
        const result = await this.rpc({
            model: "date.range",
            method: "search_read",
            fields: ["name", "type_id", "date_start", "date_end"],
            context: session.user_context,
        });
        result.forEach((range) => {
            const range_type = range.type_id[0];
            if (this.date_ranges[range_type] === undefined) {
                const r = {
                    symbol: "between",
                    description: `${_lt("in")} ${range.type_id[1]}`,
                    date_range: true,
                    date_range_type: range_type,
                };
                this.OPERATORS.date.push(r);
                this.OPERATORS.datetime.push(r);
                this.date_ranges[range_type] = [];
            }
            this.date_ranges[range_type].push(range);
        });
    },

    _setDefaultValue(condition) {
        const type = this.fields[condition.field].type;
        const operator = this.OPERATORS[FIELD_TYPES[type]][condition.operator];
        if (operator.date_range) {
            const default_range = this.date_ranges[operator.date_range_type][0];
            const d_start = moment(`${default_range.date_start} 00:00:00`);
            const d_end = moment(`${default_range.date_end} 23:59:59`);
            condition.value = [d_start, d_end];
        } else {
            this._super(...arguments);
        }
    },

    onValueChange(condition, ev) {
        const type = this.fields[condition.field].type;
        const operator = this.OPERATORS[FIELD_TYPES[type]][condition.operator];
        if (operator.date_range) {
            const eid = parseInt(ev.target.value);
            const ranges = this.date_ranges[operator.date_range_type];
            const range = ranges.find((x) => x.id == eid);
            const d_start = moment.utc(`${range.date_start} 00:00:00`);
            const d_end = moment.utc(`${range.date_end} 23:59:59`);
            condition.value = [d_start, d_end];
        } else {
            this._super(...arguments);
        }
    },
});
