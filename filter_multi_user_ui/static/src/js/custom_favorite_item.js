import { patch } from "@web/core/utils/patch";
import { CustomFavoriteItem } from "@web/search/custom_favorite_item/custom_favorite_item";
import { useService } from "@web/core/utils/hooks";
import { onWillStart } from "@odoo/owl";

patch(CustomFavoriteItem.prototype, {
    setup() {
        super.setup();
        this.orm = useService("orm");
        this.state.sharedUserIds = [];
        this.state.availableUsers = [];

        onWillStart(async () => {
            this.state.availableUsers = await this.orm.searchRead(
                "res.users",
                [["share", "=", false]],
                ["id", "name"],
                { order: "name" }
            );
        });
    },

    toggleUser(userId) {
        const ids = this.state.sharedUserIds;
        if (ids.includes(userId)) {
            this.state.sharedUserIds = ids.filter((id) => id !== userId);
        } else {
            this.state.sharedUserIds = [...ids, userId];
        }
    },

    onSharedUsersChange(ev) {
        this.state.sharedUserIds = Array.from(
            ev.target.selectedOptions,
            (option) => parseInt(option.value, 10)
        );
    },

    get filteredUsers() {
        const search = (this.state.userSearch || "").toLowerCase();
        if (!search) {
            return this.state.availableUsers;
        }
        return this.state.availableUsers.filter(
            (u) => u.name.toLowerCase().includes(search)
        );
    },

    saveFavorite(ev) {
        const { isShared, sharedUserIds } = this.state;
        this.env.searchModel._abiSharedUserIds = sharedUserIds;
        return super.saveFavorite(ev);
    },
});