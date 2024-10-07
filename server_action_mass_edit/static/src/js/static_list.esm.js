/** @odoo-module **/
import {StaticList} from "@web/model/relational_model/static_list";
import {markRaw} from "@odoo/owl";
import {patch} from "@web/core/utils/patch";

patch(StaticList.prototype, {
    setup(config, data, options = {}) {
        this._parent = options.parent;
        this._onUpdate = options.onUpdate;

        this._cache = markRaw({});
        this._commands = this._commands || [];
        console.log("Initial Commands:", this._commands);

        this._savePoint = undefined;
        this._unknownRecordCommands = {};
        this._currentIds = [...this.resIds];
        this._needsReordering = false;
        this._tmpIncreaseLimit = 0;
        this._extendedRecords = new Set();

        const safeData = Array.isArray(data) ? data : [];
        this.records = safeData.slice(this.offset, this.limit).map((r) => this._createRecordDatapoint(r));

        this.count = this.resIds.length;
        this.handleField = Object.keys(this.activeFields).find(
            (fieldName) => this.activeFields[fieldName].isHandle
        );
    },

    _applyCommands() {
        console.log("Applying Commands:", this._commands);
        // Add logic here to ensure commands is iterable
        this._commands = this._commands || [];
        // Further code...
    }
});
