/* Copyright 2016 ACSONE SA/NV (<http://acsone.eu>)
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl). */
odoo.define("date_range.search_filters", function(require) {
    "use strict";

    var filters = require("web.search_filters");
    var rpc = require("web.rpc");
    var framework = require("web.framework");

    filters.ExtendedSearchProposition.include({
        select_field: function(field) {
            this._super.apply(this, arguments);
            this.is_date_range_selected = false;
            this.is_date = field.type === "date" || field.type === "datetime";
            this.$value = this.$el.find(
                ".searchview_extended_prop_value, .o_searchview_extended_prop_value"
            );
            if (this.is_date) {
                this._rpc({
                    model: "date.range.type",
                    method: "search_read",
                    fields: ["name"],
                    context: this.context,
                }).then(this.proxy("add_date_range_types_operator"));
            }
        },

        add_date_range_types_operator: function(date_range_types) {
            var self = this;
            _.each(date_range_types, function(drt) {
                var el = self.$el.find(
                    ".searchview_extended_prop_op, .o_searchview_extended_prop_op"
                );
                $("<option>", {value: "drt_" + drt.id})
                    .text(_("in ") + drt.name)
                    .appendTo(el);
            });
        },

        operator_changed: function(e) {
            var val = $(e.target).val();
            this.is_date_range_selected = val.startsWith("drt_");
            if (this.is_date_range_selected) {
                var type_id = val.replace("drt_", "");
                this.date_range_type_operator_selected(type_id);
                return;
            }
            this._super.apply(this, arguments);
        },

        date_range_type_operator_selected: function(type_id) {
            this.$value.empty().show();
            this._rpc({
                model: "date.range",
                method: "search_read",
                fields: ["name", "date_start", "date_end"],
                context: this.context,
                domain: [["type_id", "=", parseInt(type_id, 10)]],
            }).then(this.proxy("on_range_type_selected"));
        },

        on_range_type_selected: function(date_range_values) {
            this.value = new filters.ExtendedSearchProposition.DateRange(
                this,
                this.value.field,
                date_range_values
            );
            var self = this;
            this.value.appendTo(this.$value).then(function() {
                if (!self.$el.hasClass("o_filter_condition")) {
                    self.$value.find(".date-range-select").addClass("form-control");
                }
                self.value.on_range_selected();
            });
        },

        get_filter: function() {
            var res = this._super.apply(this, arguments);
            if (this.is_date_range_selected) {
                // In case of date.range, the domain is provided by the server and we don't
                // Want to put nest the returned value into an array.
                res.attrs.domain = this.value.domain;
            }
            return res;
        },
    });

    filters.ExtendedSearchProposition.DateRange = filters.Field.extend({
        template: "SearchView.extended_search.dateRange.selection",
        events: {
            change: "on_range_selected",
        },

        init: function(parent, field, date_range_values) {
            this._super(parent, field);
            this.date_range_values = date_range_values;
        },

        toString: function() {
            var select = this.$el[0];
            var option = select.options[select.selectedIndex];
            return option.label || option.text;
        },

        get_value: function() {
            return parseInt(this.$el.val(), 10);
        },

        on_range_selected: function() {
            var self = this;
            self.domain = "";
            framework.blockUI();
            return rpc
                .query({
                    args: [this.get_value()],
                    kwargs: {
                        field_name: this.field.name,
                    },
                    model: "date.range",
                    method: "get_domain",
                })
                .then(function(domain) {
                    framework.unblockUI();
                    self.domain = domain;
                });
        },

        get_domain: function() {
            return this.domain;
        },
    });
});
