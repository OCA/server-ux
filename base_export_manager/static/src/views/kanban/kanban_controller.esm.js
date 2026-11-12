import {KanbanController} from "@web/views/kanban/kanban_controller";
const {onWillRender} = owl;
import {patch} from "@web/core/utils/patch";
import {session} from "@web/session";
import {user} from "@web/core/user";

patch(KanbanController.prototype, {
    setup() {
        super.setup();
        onWillRender(async () => {
            if (this.isExportEnable) {
                const is_export_enabled =
                    session.export_models.indexOf(this.model.root.resModel) !== -1;
                if (!user.isSystem && !is_export_enabled) {
                    this.isExportEnable = false;
                }
            }
        });
    },
});
