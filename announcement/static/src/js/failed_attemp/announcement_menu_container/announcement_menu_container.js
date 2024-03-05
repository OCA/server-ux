/** @odoo-module **/
import { getMessagingComponent } from "@mail/utils/messaging_component";
const { Component } = owl;

export class AnnouncementMenuContainer extends Component {

    /**
     * @override
     */
    setup() {
        super.setup();
        this.env.services.messaging.modelManager.messagingCreatedPromise.then(() => {
            this.announcementMenuView = this.env.services.messaging.modelManager.messaging.models['AnnouncementMenuView'].insert();
            this.render();
        });
    }

}

Object.assign(AnnouncementMenuContainer, {
    components: { AnnouncementMenuView: getMessagingComponent('AnnouncementMenuView') },
    template: 'announcement.AnnouncementMenuContainer',
});
