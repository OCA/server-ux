import {Component, useState} from "@odoo/owl";
import {registry} from "@web/core/registry";
import {useService} from "@web/core/utils/hooks";

const {document} = globalThis;

export class ReviewsTable extends Component {
    setup() {
        super.setup();
        this.orm = useService("orm");
        this.state = useState({
            collapse: false,
            reviews: [],
        });
    }

    _getReviewData() {
        const records = this.env.model.root.data.review_ids.records;
        return records.map((record) => record.data);
    }

    onToggleCollapse(ev) {
        const panelHeading = ev.currentTarget.closest(".panel-heading");
        if (!panelHeading) return;
        const collapseDiv = document.getElementById("collapse1");
        if (!collapseDiv) return;
        this.state.collapse = !this.state.collapse;
        if (this.state.collapse) {
            collapseDiv.style.display = "none";
        } else {
            collapseDiv.style.display = "block";
        }
    }
}

ReviewsTable.template = "base_tier_validation.Collapse";

export const reviewsTableComponent = {
    component: ReviewsTable,
};

registry.category("fields").add("form.tier_validation", reviewsTableComponent);
