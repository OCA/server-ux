odoo.define('base_import_security_group.group_import', function (require) {
    "use strict";

    const session = require('web.session');
    const FavoriteMenu = require('web.FavoriteMenu');
    const ImportMenu = require('base_import.ImportMenu');

    class GroupImportMenu extends ImportMenu {
        async willStart() {
            var base_group = 'base_import_security_group.group_import_csv';
            this.is_export = await session.user_has_group(base_group)
        }
        mounted() {
            var $import = $('.o_import_menu')
            if (!this.is_export) {
                $import.remove()
            }
        }
    }
    FavoriteMenu.registry.add('import-menu', GroupImportMenu, 1);

});