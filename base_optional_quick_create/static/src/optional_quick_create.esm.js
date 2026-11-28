import {Many2One} from "@web/views/fields/many2one/many2one";
import {patch} from "@web/core/utils/patch";
import {session} from "@web/session";

const avoidQuickCreateModels = session.avoid_quick_create_models || [];

patch(Many2One.prototype, {
    get many2XAutocompleteProps() {
        const props = super.many2XAutocompleteProps;
        if (avoidQuickCreateModels.includes(this.props.relation)) {
            props.quickCreate = null;
        }
        return props;
    },
});
