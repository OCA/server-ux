/** @odoo-module **/

import {registry} from "@web/core/registry";
import {Dropdown} from "@web/core/dropdown/dropdown";
import {CheckBox} from "@web/core/checkbox/checkbox";
import {CustomFavoriteItem} from "@web/search/favorite_menu/custom_favorite_item";
import session from "web.session";

const favoriteMenuRegistry = registry.category("favoriteMenu");

class CustomFavoriteItemExtended extends CustomFavoriteItem {
    setup() {
        super.setup();
        this.isFiltersManager = false;
        session
            .user_has_group("base_filter_default_all_user.group_filters_manager")
            .then((has_group) => {
                this.isFiltersManager = has_group;
            });
    }

    // Override the checkbox methods to allow to check both checkbox if the user is filters manager
    /**
     * @param {boolean} checked
     */
    onDefaultCheckboxChange(checked) {
        this.state.isDefault = checked;
        if (checked && !this.isFiltersManager) {
            this.state.isShared = false;
        }
    }

    /*
     * @param {boolean} checked
     */
    onShareCheckboxChange(checked) {
        this.state.isShared = checked;
        if (checked && !this.isFiltersManager) {
            this.state.isDefault = false;
        }
    }
}

CustomFavoriteItemExtended.template = "web.CustomFavoriteItem";
CustomFavoriteItemExtended.components = {CheckBox, Dropdown};

// Unregister the original component
favoriteMenuRegistry.remove("custom-favorite-item");

// Register the extended component
favoriteMenuRegistry.add(
    "custom-favorite-item",
    {Component: CustomFavoriteItemExtended, groupNumber: 3},
    {sequence: 0}
);

export {CustomFavoriteItemExtended};
