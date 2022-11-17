/** @odoo-modules **/
/* Copyright 2022 Tecnativa - David Vidal
   License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
*/
import Dialog from "web.Dialog";
import {qweb} from "web.core";
import rpc from "web.rpc";

/**
 * @class AnnouncementDialog
 *
 * We'd like to use regular dialog, but those can be closed with ESC Key. Anyway, this
 * leaves us more freedom to shape the dialog as we want to an in v16 we'll have
 * to move to the proper OWL component.
 */
const AnnouncementDialog = Dialog.extend({
    template: "announcement.AnnouncementDialog",
    /**
     * Wait for XML dependencies and instantiate the modal structure (except
     * modal-body).
     *
     * @override
     */
    willStart: function () {
        const resize = Boolean(this._trigger_resize);
        return this._super.apply(this, arguments).then(() => {
            // Render modal once xml dependencies are loaded
            this.$modal = $(
                qweb.render("announcement.AnnouncementDialog", {
                    title: this.title,
                    subtitle: this.subtitle,
                    resize: resize,
                })
            );
            // Soft compatibility with OCAs `web_dialog_size`
            if (resize) {
                this.$modal
                    .find(".dialog_button_extend")
                    .on("click", this.proxy("_extending"));
                this.$modal
                    .find(".dialog_button_restore")
                    .on("click", this.proxy("_restore"));
                rpc.query({
                    model: "ir.config_parameter",
                    method: "announcement_full_size",
                }).then((config_full_size) => {
                    if (config_full_size) {
                        this._extending();
                        return;
                    }
                    this._restore();
                });
            }
            this.$footer = this.$modal.find(".modal-footer");
            this.set_buttons(this.buttons);
            this.$modal.on("hidden.bs.modal", _.bind(this.destroy, this));
        });
    },
});

export default AnnouncementDialog;
