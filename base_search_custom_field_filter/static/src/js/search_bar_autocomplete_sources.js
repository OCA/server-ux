odoo.define("base_search_custom_field_filter.search_inputs_related_field", function(
    require
) {
    "use strict";

    var search_bar = require("web.SearchBarAutoCompleteSources");

    search_bar.Field.include({
        _makeDomain: function(name, operator, facet) {
            var name_n = this.attrs.custom_field_filter || name;
            return this._super(name_n, operator, facet);
        },
    });

    search_bar.ManyToOneField.include({
        _makeDomain: function(name, operator, facet) {
            var name_n = this.attrs.custom_field_filter || name;
            return this._super(name_n, operator, facet);
        },
    });
});
