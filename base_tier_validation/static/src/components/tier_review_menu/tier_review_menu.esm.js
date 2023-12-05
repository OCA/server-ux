/* @odoo-module */

import {Component, useState} from "@odoo/owl";
import {Dropdown} from "@web/core/dropdown/dropdown";
import {DropdownItem} from "@web/core/dropdown/dropdown_item";
import {registry} from "@web/core/registry";
import {useDiscussSystray} from "@mail/utils/common/hooks";
import {useService} from "@web/core/utils/hooks";

const systrayRegistry = registry.category("systray");

export class TierReviewMenu extends Component {
    setup() {
        this.discussSystray = useDiscussSystray();
        this.orm = useService("orm");
        this.store = useState(useService("mail.store"));
        this.action = useService("action");
        this.fetchSystrayReviewer();
    }
    async fetchSystrayReviewer() {
        const groups = await this.orm.call("res.users", "review_user_count");
        let total = 0;
        for (const group of groups) {
            total += group.pending_count || 0;
        }
        this.store.tierReviewCounter = total;
        this.store.tierReviewGroups = groups;
    }
    onBeforeOpen() {
        this.fetchSystrayReviewer();
    }
    availableViews() {
        return [
            [false, "kanban"],
            [false, "list"],
            [false, "form"],
            [false, "activity"],
        ];
    }
    openReviewGroup(group) {
        document.body.click(); // Hack to close dropdown
        const context = {};
        var domain = [["can_review", "=", true]];
        if (group.active_field) {
            domain.push(["active", "in", [true, false]]);
        }
        const views = this.availableViews();

        this.action.doAction(
            {
                context,
                domain,
                name: group.name,
                res_model: group.model,
                search_view_id: [false],
                type: "ir.actions.act_window",
                views,
            },
            {
                clearBreadcrumbs: true,
            }
        );
    }
}

TierReviewMenu.template = "base_tier_validation.TierReviewMenu";
TierReviewMenu.components = {Dropdown, DropdownItem};
TierReviewMenu.props = [];

export const systrayItem = {Component: TierReviewMenu};

systrayRegistry.add("base_tier_validation.ReviewerMenu", systrayItem, {sequence: 99});
