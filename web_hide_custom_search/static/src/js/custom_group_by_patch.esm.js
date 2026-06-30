odoo.define("web_hide_custom_search.CustomGroupByItemPatch", function (require) {
    const CustomGroupByItem = require("web.CustomGroupByItem");
    const {patch} = require("web.utils");
    const {hooks, useState} = owl;
    const {onWillStart} = hooks;
    const rpc = require("web.rpc");

    patch(
        CustomGroupByItem.prototype,
        "web_hide_custom_search.CustomGroupByItemPatch",
        {
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
        }
    );
});
