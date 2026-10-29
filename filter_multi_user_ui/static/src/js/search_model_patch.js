import { patch } from "@web/core/utils/patch";
import { SearchModel } from "@web/search/search_model";
import { user } from "@web/core/user";

patch(SearchModel.prototype, {
    _getIrFilterDescription(params = {}) {
        const result = super._getIrFilterDescription(params);
        if (this._abiSharedUserIds && this._abiSharedUserIds.length) {
            const ids = [...new Set([...this._abiSharedUserIds, user.userId])];
            result.irFilter.manual_user_ids = [[6, 0, ids]];
            this._abiSharedUserIds = null;
        }
        return result;
    },
});