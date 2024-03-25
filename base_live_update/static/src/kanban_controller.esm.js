/** @odoo-module **/

import {KanbanController} from "@web/views/kanban/kanban_controller";
import {patch} from "web.utils";
import {useLiveUpdate} from "@base_live_update/base_live_update.esm";

patch(KanbanController.prototype, "kanban_live_update", {
    setup() {
        this._super(...arguments);
        const model = this.model.rootParams.resModel;
        useLiveUpdate(this.env.bus, model, this._handle_live_update.bind(this));
    },
    async _handle_live_update({type, detail}) {
        const records = this.model.root.records;
        switch (type.split(":")[2]) {
            case "write": {
                const updated = records.filter((r) => detail.__ids.includes(r.resId));
                for (const record of updated) {
                    await record.load();
                    // TODO the below would be nicer, but then we need to
                    // deal with nonstored fields, and convert values
                    // await record.update(detail);
                }
                break;
            }
            case "unlink": {
                const deleted = records.filter((r) => detail.includes(r.resId));
                for (const record of deleted) {
                    this.model.root.removeRecord(record);
                }
                break;
            }
            case "create": {
                for (const [resId] of detail) {
                    // TODO this should check if the new record is entailed by the
                    // currently active domain
                    this.model.root.addExistingRecord(resId);
                }
                break;
            }
        }
        for (const group of this.model.root.groups || []) {
            // TODO this should be smarter and add/remove records
            // to/from groups based on the updates we did above
            await group.load();
        }
        this.model.notify();
        return this.render(true);
    },
});
