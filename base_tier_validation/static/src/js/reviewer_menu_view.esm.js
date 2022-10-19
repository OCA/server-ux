/** @odoo-module **/

import {useComponentToModel} from "@mail/component_hooks/use_component_to_model";
import {registerMessagingComponent} from "@mail/utils/messaging_component";

const {Component} = owl;

export class ReviewerMenuView extends Component {
    /**
     * @override
     */
    setup() {
        super.setup();
        useComponentToModel({fieldName: "component"});
    }
    /**
     * @returns {ReviewerMenuView}
     */
    get reviewerMenuView() {
        return this.props.record;
    }
}

Object.assign(ReviewerMenuView, {
    props: {record: Object},
    template: "base_tier_validation.ReviewerMenuView",
});

registerMessagingComponent(ReviewerMenuView);
