odoo.define("web_hide_custom_search.web.CustomFilterItemPatch", function (require) {
    const CustomFilterItem = require("web.CustomFilterItem");
    const {patch} = require("web.utils");
    const {hooks, useState} = owl;
    const {onWillStart} = hooks;
    const rpc = require("web.rpc");

    patch(CustomFilterItem.prototype, "web_hide_custom_search.CustomFilterItemPatch", {
        setup() {
            this._super.apply(this, arguments);
            this.visibleState = useState({isVisible: true});

            onWillStart(async () => {
                const modelName = this.model.config.modelName;
                const isVisible = await rpc.query({
                    model: "ir.model",
                    method: "is_custom_search_visible",
                    args: [modelName],
                });
                this.visibleState.isVisible = isVisible;
            });
        },
    });
});
