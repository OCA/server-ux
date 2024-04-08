/** @odoo-module **/

import {Domain} from "@web/core/domain";
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
                    await this.model.mutex.exec(async () => {
                        const group = (this.model.root.groups || []).find((g) =>
                            g.records.includes(record)
                        );
                        await record.load();
                        // TODO the below would be nicer, but then we need to
                        // deal with nonstored fields, and convert values
                        // await record.update(detail);
                        const new_group = (this.model.root.groups || []).find((g) =>
                            new Domain(g.groupDomain).contains(record.dataContext)
                        );
                        if (group && new_group && new_group !== group) {
                            group.records.splice(group.records.indexOf(record), 1);
                            new_group.records.splice(0, 0, record);
                        }
                    });
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
                for (const [resId, data] of detail) {
                    for (const group of this.model.root.groups || [this.model.root]) {
                        if (
                            new Domain(group.groupDomain || group.domain).contains(data)
                        ) {
                            await group.addExistingRecord(resId);
                            break;
                        }
                    }
                }
                break;
            }
        }
        this.model.notify();
        return this.render(true);
    },
});
