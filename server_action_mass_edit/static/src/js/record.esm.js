/** @odoo-module **/
import {Record} from "@web/model/relational_model/record";
import {patch} from "@web/core/utils/patch";

patch(Record.prototype, {
    _createStaticListDatapoint(data, fieldName) {
        const {related, limit, defaultOrderBy} = this.activeFields[fieldName];
        const config = {
            resModel: this.fields[fieldName].relation,
            activeFields: (related && related.activeFields) || {},
            fields: (related && related.fields) || {},
            relationField: this.fields[fieldName].relation_field || false,
            offset: 0,
            // To prevent the TypeError: data.map is not a function while set/remove/add
            // value in wizard
            resIds: Array.isArray(data) ? data.map((r) => r.id || null) : [],
            orderBy: defaultOrderBy || [],
            limit: limit || Number.MAX_SAFE_INTEGER,
            currentCompanyId: this.currentCompanyId,
            context: {},
        };
        const options = {
            onUpdate: ({withoutOnchange} = {}) =>
                this._update({[fieldName]: []}, {withoutOnchange}),
            parent: this,
        };
        return new this.model.constructor.StaticList(this.model, config, data, options);
    },
});
