/** @odoo-module **/

import { useComponentToModel } from '@mail/component_hooks/use_component_to_model';
import { registerMessagingComponent } from '@mail/utils/messaging_component';

const { Component } = owl;

export class AnnouncementMenuView extends Component {
    /**
     * @override
     */
     setup() {
        super.setup();
        useComponentToModel({ fieldName: 'component' });
    }
    /**
     * @returns {AnnouncementMenuView}
     */
    get announcementMenuView() {
        return this.props.record;
    }
}

Object.assign(AnnouncementMenuView, {
    props: { record: Object },
    template: 'announcement.AnnouncementMenuView',
});

registerMessagingComponent(AnnouncementMenuView);
