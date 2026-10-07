/**
 * Copyright 2026 CIT Services
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
 */

import {Cache} from "@web/core/utils/cache";
import {rpc} from "@web/core/network/rpc";

async function fetchArchiveAccess(resModel) {
    const result = await rpc("/web/dataset/call_kw", {
        model: "ir.model.access",
        method: "get_archive_access",
        args: [resModel],
        kwargs: {},
    });
    return result;
}
export const archiveAccessCache = new Cache(fetchArchiveAccess, (model) => model);
