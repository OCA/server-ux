import {Plugin, onWillStart, usePlugin} from "@odoo/owl";
import {ORM} from "@web/core/orm_plugin";

/**
 * Holds the date ranges and date range types shown by the domain editor.
 *
 * OWL 3 has no sub env: the DomainSelector provides this plugin to its own
 * subtree (providePlugins) and the TreeEditor below reads it from its scope.
 */
export class DateRangePlugin extends Plugin {
    static id = "date_range.DateRangePlugin";

    orm = usePlugin(ORM);
    dateRanges = [];
    dateRangeTypes = [];

    setup() {
        onWillStart(async () => {
            [this.dateRanges, this.dateRangeTypes] = await Promise.all([
                this.orm.call("date.range", "search_read", []),
                this.orm.call("date.range.type", "search_read", []),
            ]);
        });
    }
}
