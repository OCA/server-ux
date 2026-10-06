import {PivotRenderer} from "@web/views/pivot/pivot_renderer";
const {onWillRender} = owl;
import {patch} from "@web/core/utils/patch";
import {session} from "@web/session";

patch(PivotRenderer.prototype, {
    setup() {
        super.setup();
        this.isExportEnable = true;
        onWillRender(() => {
            const is_export_enabled =
                session.export_models.indexOf(this.model.metaData.resModel) !== -1;
            if (!session.is_system && !is_export_enabled) {
                this.isExportEnable = false;
            }
        });
    },
});
