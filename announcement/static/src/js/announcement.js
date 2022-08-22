odoo.define("announcement.systray", function(require) {
    "use strict";

    require("web.dom_ready");
    const core = require("web.core");
    const session = require("web.session");
    const SystrayMenu = require("web.SystrayMenu");
    const Widget = require("web.Widget");
    const AnnouncementDialog = require("announcement.AnnouncementDialog");

    const QWeb = core.qweb;
    const _t = core._t;

    const AnnouncementMenu = Widget.extend({
        template: "announcement.AnnouncementMenu",
        events: {
            "show.bs.dropdown": "_onAnnouncementMenuShow",
            "click .o_mail_preview": "_onAnnouncementClick",
        },
        start: function() {
            this.$announcement_preview = this.$(".o_mail_systray_dropdown_items");
            this._updateAnnouncementPreview();
            this.call("bus_service", "addChannel", "announcement");
            this.call("bus_service", "startPolling");
            this.call(
                "bus_service",
                "onNotification",
                this,
                this._updateAnnouncementPreview
            );
            let popup_announcement = false;
            // Let's check if the user just logged in and to decide if we popup the
            // announcements. This delay is hardcoded to 5 minutes, although we could
            // allow to configure it in the future.
            this._rpc({
                model: "res.users",
                method: "read",
                args: [session.uid, ["login_date"]],
            }).then(user => {
                const login_date = !_.isEmpty(user) && user[0].login_date;
                const minutes_since_last_login =
                    (moment.utc(new Date()).valueOf() -
                        moment.utc(login_date).valueOf()) /
                    1000 /
                    60;
                popup_announcement = Boolean(minutes_since_last_login < 5);
            });
            // When the user logs in we show him his unread announcements
            const _this = this;
            function waitAndCheck() {
                if (odoo.isReady) {
                    _this._getAnnouncementData().then(() => {
                        if (popup_announcement && !_.isEmpty(_this.announcements)) {
                            _this.announcements[0].dialog.open();
                        }
                    });
                } else {
                    setTimeout(waitAndCheck, 500);
                }
            }
            setTimeout(waitAndCheck, 500);
            return this._super();
        },

        // Private

        /**
         * Make RPC and get current user's activity details
         * @private
         * @returns {integer}
         */
        _getAnnouncementData: function() {
            return this._rpc({
                model: "res.users",
                method: "announcement_user_count",
                kwargs: {
                    context: session.user_context,
                },
            }).then(data => {
                this._prepareAnnouncementData(data || []);
                this.announcements = data;
                this.announcementCounter = this.announcements.length;
                this.$(".o_notification_counter").text(this.announcementCounter);
                this.$el.toggleClass("o_no_notification", !this.announcementCounter);
            });
        },
        /**
         * Update(render) announcement system tray view on announcement refresh
         * @private
         */
        _updateAnnouncementPreview: function() {
            this._getAnnouncementData().then(() => {
                const render_context = {
                    announcements: this.announcements,
                    pending_count: this.announcementCounter,
                };
                this.$announcement_preview.html(
                    QWeb.render("announcement.AnnouncementMenuPreview", render_context)
                );
            });
        },
        /**
         * Update counter based on announcement status
         * @private
         * @param {Object} [data] key, value to decide announcement read or unread
         * @param {String} [data.type] notification type
         * @param {Boolean} [data.announcement_unread] when announcement unread
         * @param {Boolean} [data.activity_created] when announcement gets read
         */
        _updateCounter: function(data) {
            if (data) {
                if (data.announcement_unread) {
                    this.announcementCounter++;
                }
                if (data.announcement_read && this.announcementCounter > 0) {
                    this.announcementCounter--;
                }
                this.$(".o_notification_counter").text(this.announcementCounter);
                this.$el.toggleClass("o_no_notification", !this.announcementCounter);
            }
        },
        /**
         * Prepare the announcements data so we can work with them properly (attach
         * popup classes, get the next and previous ids for proper navigation, etc.)
         * @private
         * @param {Object} data
         */
        _prepareAnnouncementData: function(data) {
            _.each(data, a => {
                const index = _.indexOf(data, a);
                // We make it as an infinite loop so the last announcement next slide
                // is the first announcement.
                const previous_announcement_id =
                    data[index - 1] || data[data.length - 1];
                const next_announcement_id = data[index + 1] || data[0];
                a.next_announcement_id =
                    next_announcement_id && next_announcement_id.id;
                // This one is not being used but it could be handy in future features.
                a.previous_announcement_id =
                    previous_announcement_id && previous_announcement_id.id;
                a.dialog = this._buildAnnouncementDialog(a);
            });
        },
        /**
         * @private
         * @param {id} announcement
         * @returns
         */
        _getAnnouncementById: function(id) {
            return this.announcements.filter(a => {
                return a.id === id && a;
            })[0];
        },
        /**
         * @private
         * @param {id} announcement
         * @returns
         */
        _openAnnouncemenId: function(id) {
            const announcement = this._getAnnouncementById(id);
            // The announcement could be already destroyed
            if (_.isEmpty(announcement)) {
                return;
            }
            this._getAnnouncementById(id).dialog.open();
        },
        /**
         * Build announcement popup
         * @private
         * @param {Object} announcement
         * @returns {Object} dialog - standard odoo dialog
         */
        _buildAnnouncementDialog: function(announcement) {
            const next_announcement = announcement.next_announcement_id;
            const dialog = new AnnouncementDialog(this, {
                title: announcement.name,
                buttons: [
                    {
                        text: _t("Mark as read"),
                        classes: "btn-primary",
                        close: true,
                        click: () => {
                            this._rpc({
                                model: "res.users",
                                method: "mark_announcement_as_read",
                                args: [announcement.id],
                                kwargs: {
                                    context: session.user_context,
                                },
                            })
                                .then(() => {
                                    this._updateAnnouncementPreview();
                                })
                                .then(() => {
                                    // As the announcement list is chained in a loop we want
                                    // to avoid opening the same announcement we just closed
                                    if (announcement.id !== next_announcement) {
                                        this._openAnnouncemenId(next_announcement);
                                    }
                                });
                        },
                    },
                ],
                $content: $("<section />").append($(announcement.content)),
            });
            return dialog;
        },

        // ------------------------------------------------------------
        // Handlers
        // ------------------------------------------------------------

        /**
         * Show announcement popup
         * @private
         * @param {MouseEvent} event
         */
        _onAnnouncementClick: function(event) {
            const data = $(event.currentTarget).data();
            const announcement = this._getAnnouncementById(data.id);
            announcement.dialog.open();
        },
        /**
         * When menu clicked update activity preview if counter updated
         * @private
         * @param {MouseEvent} event
         */
        _onAnnouncementMenuShow: function() {
            this._updateAnnouncementPreview();
        },
    });

    SystrayMenu.Items.push(AnnouncementMenu);

    return AnnouncementMenu;
});
