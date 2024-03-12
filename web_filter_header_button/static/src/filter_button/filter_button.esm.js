/** @odoo-module **/
const {Component} = owl;

export class FilterButton extends Component {
    setup() {
        this.model = this.env.searchModel;
    }
    shownFilters(filters) {
        return filters.filter((filter) => {
            return filter.context && filter.context.shown_in_panel;
        });
    }
    /*
     */
    mapFilterType(filter) {
        const mapping = {
            filter: {
                color: "primary",
            },
            favorite: {
                color: "warning",
            },
        };
        return mapping[filter.type];
    }
    onClickReset() {
        this.model.dispatch("clearQuery");
    }
    onToggleFilter(filter) {
        this.model.dispatch("toggleFilter", filter.id);
    }
}
FilterButton.template = "filter_button.FilterButton";
