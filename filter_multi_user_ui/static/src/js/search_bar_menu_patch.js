import { patch } from "@web/core/utils/patch";
import { SearchBarMenu } from "@web/search/search_bar_menu/search_bar_menu";
import { useService } from "@web/core/utils/hooks";

patch(SearchBarMenu.prototype, {
    setup() {
        super.setup();
        this.actionService = useService("action");
    },

    openFilterUsers(item) {
        this.actionService.doAction({
            type: "ir.actions.act_window",
            res_model: "ir.filters",
            res_id: item.serverSideId,
            views: [[false, "form"]],
            target: "new",
        });
    },
});