/** @odoo-module **/

import {patch} from "@web/core/utils/patch";
import rpc from "web.rpc";
import {CustomFilterItem} from "@web/search/filter_menu/custom_filter_item";
const {hooks, useState} = owl;
const {onWillStart} = hooks;

patch(
    CustomFilterItem.prototype,
    "web_hide_custom_search.search.CustomFilterItemPatch",
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
