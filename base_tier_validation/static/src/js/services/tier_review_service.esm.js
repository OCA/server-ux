/** @odoo-module **/

import {registry} from "@web/core/registry";

export class TierReviewService {
    constructor(env, services) {
        this.env = env;
        this.store = services["mail.store"];
        this.busService = services.bus_service;
    }
    setup() {
        this.busService.subscribe("base.tier.validation/updated", (payload) => {
            if (payload.review_created) {
                this.store.tierReviewCounter++;
            }
            if (payload.review_deleted) {
                this.store.tierReviewCounter--;
            }
        });
        this.busService.start();
    }
}

export const tierReviewService = {
    dependencies: ["bus_service", "mail.store"],

    start(env, services) {
        const tier_review_service = new TierReviewService(env, services);
        tier_review_service.setup(env, services);
        return tier_review_service;
    },
};

registry.category("services").add("tierReviewService", tierReviewService);
