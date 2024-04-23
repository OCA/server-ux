/** @odoo-module **/

import {CustomFavoriteItemExtended} from "@base_filter_default_all_user/search/favorite_menu/custom_favorite_item";

let customFavoriteItemExtended;

async function toggleDefaultCheckBox() {
    const checkbox = document.querySelector(
        '.o_add_favorite .form-check input[type="checkbox"]'
    );
    checkbox.checked = !checkbox.checked;
    await triggerEvent(checkbox, "change");
}

async function toggleShareCheckBox() {
    const checkbox = document.querySelectorAll(
        '.o_add_favorite .form-check input[type="checkbox"]'
    )[1];
    checkbox.checked = !checkbox.checked;
    await triggerEvent(checkbox, "change");
}

QUnit.module(
    "CustomFavoriteItemExtended",
    {
        beforeEach: function () {
            customFavoriteItemExtended = new CustomFavoriteItemExtended();
        },
        afterEach: function () {
            customFavoriteItemExtended = null;
        },
    },
    function () {
        QUnit.test(
            "onDefaultCheckboxChange should set isShared to false if not filters manager and checked",
            async function (assert) {
                // Arrange
                customFavoriteItemExtended.isFiltersManager = false;
                await toggleShareCheckBox();
                // Act
                await toggleDefaultCheckBox();

                // Assert
                assert.notOk(
                    customFavoriteItemExtended.state.isShared,
                    "isShared should be false"
                );
            }
        );

        QUnit.test(
            "onDefaultCheckboxChange should not change isShared if filters manager and checked",
            async function (assert) {
                // Arrange
                customFavoriteItemExtended.isFiltersManager = true;
                await toggleShareCheckBox();

                // Act
                await toggleDefaultCheckBox();

                // Assert
                assert.ok(
                    customFavoriteItemExtended.state.isShared,
                    "isShared should remain true"
                );
            }
        );

        QUnit.test(
            "onShareCheckboxChange should set isDefault to false if not filters manager and checked",
            async function (assert) {
                // Arrange
                customFavoriteItemExtended.isFiltersManager = false;
                await toggleDefaultCheckBox();

                // Act
                await toggleShareCheckBox();

                // Assert
                assert.notOk(
                    customFavoriteItemExtended.state.isDefault,
                    "isDefault should be false"
                );
            }
        );

        QUnit.test(
            "onShareCheckboxChange should not change isDefault if filters manager and checked",
            async function (assert) {
                // Arrange
                customFavoriteItemExtended.isFiltersManager = true;
                await toggleDefaultCheckBox();

                // Act
                await toggleShareCheckBox();

                // Assert
                assert.ok(
                    customFavoriteItemExtended.state.isDefault,
                    "isDefault should remain true"
                );
            }
        );
    }
);
