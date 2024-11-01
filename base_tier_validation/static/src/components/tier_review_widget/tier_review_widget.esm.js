import {Component, onMounted} from "@odoo/owl";

import {ensureJQuery} from "@web/core/ensure_jquery";
import {registry} from "@web/core/registry";
import {useService} from "@web/core/utils/hooks";

export class ReviewsTable extends Component {
    setup() {
        super.setup();
        this.collapse = false;
        this.orm = useService("orm");
        this.reviews = [];

        onMounted(async () => {
            await ensureJQuery();
        });
    }

    _getReviewData() {
        const records = this.env.model.root.data.review_ids.records;
        return records.map((record) => record.data);
    }

    onToggleCollapse(ev) {
        var $panelHeading = $(ev.currentTarget).closest(".panel-heading");
        if (this.collapse) {
            $panelHeading.next("div#collapse1").hide();
        } else {
            $panelHeading.next("div#collapse1").show();
        }
        this.collapse = !this.collapse;
    }
}

ReviewsTable.template = "base_tier_validation.Collapse";

export const reviewsTableComponent = {
    component: ReviewsTable,
};

registry.category("fields").add("form.tier_validation", reviewsTableComponent);
