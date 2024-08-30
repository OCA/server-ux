/** @odoo-module **/
import {StaticList} from "@web/model/relational_model/static_list";
import {markRaw} from "@odoo/owl";
import {patch} from "@web/core/utils/patch";

patch(StaticList.prototype, {
    setup(config, data, options = {}) {
        this._parent = options.parent;
        this._onUpdate = options.onUpdate;

        this._cache = markRaw({});
        this._commands = [];
        this._initialCommands = [];
        this._savePoint = undefined;
        this._unknownRecordCommands = {};
        this._currentIds = [...this.resIds];
        this._initialCurrentIds = [...this.currentIds];
        this._needsReordering = false;
        this._tmpIncreaseLimit = 0;
        this._extendedRecords = new Set();
        // To prevent the TypeError: data.slice is not a function" while set/remove/add
        // value in wizard
        this.records = Array.isArray(data)
            ? data
                  .slice(this.offset, this.limit)
                  .map((r) => this._createRecordDatapoint(r))
            : [];
        this.count = this.resIds.length;
        this.handleField = Object.keys(this.activeFields).find(
            (fieldName) => this.activeFields[fieldName].isHandle
        );
    },
});
