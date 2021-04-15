/* Copyright 2016 ACSONE SA/NV (<https://acsone.eu>)
 * Copyright 2021 Studio73 - Pablo Fuentes (https://www.studio73.es)
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

odoo.define("date_range.CustomFilterItem", function (require) {
    "use strict";

    const {_lt} = require("web.core");
    const session = require("web.session");
    const {FIELD_OPERATORS, FIELD_TYPES} = require("web.searchUtils");
    const CustomFilterItem = require("web.CustomFilterItem");

    CustomFilterItem.patch(
        "date_range.CustomFilterItem",
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
                    const operator = this.OPERATORS[FIELD_TYPES[type]][
                        condition.operator
                    ];
                    if (operator.date_range) {
                        const default_range = this.date_ranges[
                            operator.date_range_type
                        ][0];
                        const d_start = moment(`${default_range.date_start} 00:00:00`);
                        const d_end = moment(`${default_range.date_end} 23:59:59`);
                        condition.value = [d_start, d_end];
                    } else {
                        super._setDefaultValue(...arguments);
                    }
                }

                _onValueInput(condition, ev) {
                    const type = this.fields[condition.field].type;
                    const operator = this.OPERATORS[FIELD_TYPES[type]][
                        condition.operator
                    ];
                    if (operator.date_range) {
                        const eid = parseInt(ev.target.value);
                        const ranges = this.date_ranges[operator.date_range_type];
                        const range = ranges.find((x) => x.id == eid);
                        const d_start = moment(`${range.date_start} 00:00:00`);
                        const d_end = moment(`${range.date_end} 23:59:59`);
                        condition.value = [d_start, d_end];
                    } else {
                        super._onValueInput(...arguments);
                    }
                }
            }
    );

    return CustomFilterItem;
});
