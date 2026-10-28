import {ListController} from "@web/views/list/list_controller";
const {onWillRender} = owl;
import {exportAllItem} from "@web/views/list/export_all/export_all";
import {patch} from "@web/core/utils/patch";
import {session} from "@web/session";
import {user} from "@web/core/user";

function isExportAllowed(resModel) {
    return user.isSystem || session.export_models.indexOf(resModel) !== -1;
}

patch(ListController.prototype, {
    setup() {
        super.setup();
        onWillRender(async () => {
            if (this.isExportEnable && !isExportAllowed(this.model.root.resModel)) {
                this.isExportEnable = false;
            }
        });
    },
});

patch(exportAllItem, {
    async isDisplayed(env) {
        return (
            (await super.isDisplayed(env)) && isExportAllowed(env.model.root.resModel)
        );
    },
});
