import {Record} from "@web/model/relational_model/record";
import {patch} from "@web/core/utils/patch";

patch(Record.prototype, {
    _createStaticListDatapoint(data, fieldName, options) {
        // The dynamic x2many fields of the mass editing wizard get False
        // instead of a list of records, which crashes the StaticList
        // ("data.map is not a function") while setting/removing/adding values.
        return super._createStaticListDatapoint(
            Array.isArray(data) ? data : [],
            fieldName,
            options
        );
    },
});
