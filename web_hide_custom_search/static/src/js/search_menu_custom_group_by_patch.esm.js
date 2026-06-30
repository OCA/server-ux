/** @odoo-module **/

import {patch} from "@web/core/utils/patch";
import rpc from "web.rpc";
import {CustomGroupByItem} from "@web/search/group_by_menu/custom_group_by_item";
const {hooks, useState} = owl;
const {onWillStart} = hooks;

patch(
    CustomGroupByItem.prototype,
    "web_hide_custom_search.search.CustomGroupByItemPatch",
    {
        setup() {
            this._super(...arguments);
            this.visibleState = useState({isVisible: true});

            onWillStart(async () => {
                const modelName = this.env.searchModel.resModel;
                const isVisible = await rpc.query({
                    model: "ir.model",
                    method: "is_custom_search_visible",
                    args: [modelName],
                });
                this.visibleState.isVisible = isVisible;
            });
        },
    }
);
