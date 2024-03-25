/** @odoo-module **/
import {registry} from "@web/core/registry";
import {useBus} from "@web/core/utils/hooks";

const CHANNEL_PREFIX = "live.update.";

export const liveUpdateService = {
    dependencies: ["bus_service"],

    start(env, {bus_service}) {
        this.bus_service = bus_service;
        this.env = env;
        for (const model in registry.category("live_update_models").content) {
            this._handleModelSubscription({detail: {operation: "add", key: model}});
        }
        registry
            .category("live_update_models")
            .addEventListener("UPDATE", this._handleModelSubscription.bind(this));
        bus_service.addEventListener(
            "notification",
            this._handleNotifications.bind(this)
        );
        bus_service.start();
    },

    async _handleNotifications({detail: notifications}) {
        for (const {payload, type} of notifications) {
            if (type === "live.update") {
                this.env.bus.trigger(
                    "live_update:" + payload.model + ":" + payload.action,
                    payload.data
                );
            }
        }
    },

    async _handleModelSubscription({detail: {operation, key: model}}) {
        switch (operation) {
            case "add":
                this.bus_service.addChannel(CHANNEL_PREFIX + model);
                break;
            case "delete":
                this.env.bus_service.deleteChannel(CHANNEL_PREFIX + model);
                break;
        }
    },
};

export function useLiveUpdate(bus, model, callback) {
    if (!registry.category("live_update_models").contains(model)) {
        registry.category("live_update_models").add(model);
    }
    useBus(bus, "live_update:" + model + ":write", callback);
    useBus(bus, "live_update:" + model + ":create", callback);
    useBus(bus, "live_update:" + model + ":unlink", callback);
}

registry.category("services").add("liveUpdate", liveUpdateService);
