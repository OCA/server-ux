/** @odoo-module **/

import {systrayService} from "@base_tier_validation/js/systray_service.esm";

import {registry} from "@web/core/registry";

const serviceRegistry = registry.category("services");
serviceRegistry.add("review_systray_service", systrayService);
