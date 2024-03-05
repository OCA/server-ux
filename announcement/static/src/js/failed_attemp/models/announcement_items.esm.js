/** @odoo-module **/

import {attr, many, one} from "@mail/model/model_field";
import {registerModel} from "@mail/model/model_core";

registerModel({
    name: "AnnouncementItem",
    modelMethods: {
        convertData(data) {
            return {
                content: data.content,
                id: data.id,
                name: data.name,
            };
        },
    },
    recordMethods: {
        /**
         * @private
         */
        _onChangePendingCount() {
            if (this.type === "announcement" && this.pending_count === 0) {
                this.delete();
            }
        },
    },
    fields: {
        announcementItemViews: many("AnnouncementItemView", {
            inverse: "announcementItem",
        }),
        domain: attr(),
        irModel: one("ir.model.announcement", {
            identifying: true,
            inverse: "announcementItem",
        }),
        pending_count: attr({
            default: 0,
        }),
        type: attr(),
    },
    onChanges: [
        {
            dependencies: ["pending_count", "type"],
            methodName: "_onChangePendingCount",
        },
    ],
});
