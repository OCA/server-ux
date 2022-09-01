/** @odoo-module **/
import {FIELD_OPERATORS, FIELD_TYPES} from "web.searchUtils";
import CustomFilterItem from "web.CustomFilterItem";
import {_lt} from "@web/core/l10n/translation";
import {patch} from "web.utils";
import {session} from "@web/session";

patch(
    CustomFilterItem.prototype,
    "date_range/static/src/js/date_range.esm.js",
    (T) =>
        class extends T {
            constructor() {
                super(...arguments);
                this._computeDateRangeOperators();
            }

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
            }

            _setDefaultValue(condition) {
                const type = this.fields[condition.field].type;
                const operator = this.OPERATORS[FIELD_TYPES[type]][condition.operator];
                if (operator.date_range) {
                    const default_range = this.date_ranges[operator.date_range_type][0];
                    const d_start = moment(`${default_range.date_start} 00:00:00`);
                    const d_end = moment(`${default_range.date_end} 23:59:59`);
                    condition.value = [d_start, d_end];
                } else {
                    super._setDefaultValue(...arguments);
                }
            }

            _onValueInputChange(condition, ev) {
                const type = this.fields[condition.field].type;
                const operator = this.OPERATORS[FIELD_TYPES[type]][condition.operator];
                if (operator.date_range) {
                    /* eslint-disable radix */
                    const eid = parseInt(ev.target.value);
                    const ranges = this.date_ranges[operator.date_range_type];
                    const range = ranges.find((x) => x.id === eid);
                    const d_start = moment(`${range.date_start} 00:00:00`);
                    const d_end = moment(`${range.date_end} 23:59:59`);
                    condition.value = [d_start, d_end];
                } else {
                    super._onValueInputChange(...arguments);
                }
            }
        }
);

export default CustomFilterItem;
