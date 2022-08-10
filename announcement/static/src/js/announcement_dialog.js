odoo.define("announment.AnnouncementDialog", function(require) {
    "use strict";

    const core = require("web.core");
    const Dialog = require("web.Dialog");

    const QWeb = core.qweb;

    /**
     * @class AnnouncementDialog
     *
     * We'd like to use regular dialog, but those can be closed with ESC Key. Anyway, this
     * leaves us more freedom to shape the dialog as we want to.
     */
    var AnnouncementDialog = Dialog.extend({
        template: "announcement.AnnouncementDialog",
        /**
         * Wait for XML dependencies and instantiate the modal structure (except
         * modal-body).
         *
         * @override
         */
        willStart: function() {
            const resize = Boolean(this._trigger_resize);
            return this._super.apply(this, arguments).then(() => {
                // Render modal once xml dependencies are loaded
                this.$modal = $(
                    QWeb.render("announcement.AnnouncementDialog", {
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
                    this._restore();
                }
                this.$footer = this.$modal.find(".modal-footer");
                this.set_buttons(this.buttons);
                this.$modal.on("hidden.bs.modal", _.bind(this.destroy, this));
            });
        },
    });

    return AnnouncementDialog;
});
