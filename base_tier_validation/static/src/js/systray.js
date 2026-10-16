/* Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
   License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */
odoo.define("tier_validation.systray", function (require) {
    "use strict";

    var core = require("web.core");
    var session = require("web.session");
    var SystrayMenu = require("web.SystrayMenu");
    var Widget = require("web.Widget");

    var QWeb = core.qweb;

    var ReviewMenu = Widget.extend({
        template: "tier.validation.ReviewMenu",
        events: {
            "show.bs.dropdown": "_onReviewMenuShow",
            "click .o_mail_activity_action": "_onReviewActionClick",
            "click .o_mail_preview": "_onReviewFilterClick",
        },
        start: function () {
            this.$reviews_preview = this.$(".o_mail_systray_dropdown_items");
            this._updateReviewPreview();
            this.channel = "base.tier.validation";
            this.call("bus_service", "addChannel", this.channel);
            this.call("bus_service", "startPolling");
            this.call("bus_service", "onNotification", this, this.bus_notification);
            return this._super();
        },

        bus_notification: function (notifications) {
            var self = this;
            var reviewChanged = _.some(notifications, function (notification) {
                return notification[0] === self.channel;
            });
            if (reviewChanged) {
                self._updateReviewPreview();
            }
        },
        // Private

        /**
         * Make RPC and get current user's activity details
         * @private
         * @returns {integer}
         */
        _getReviewData: function () {
            var self = this;

            return self
                ._rpc(
                    {
                        model: "res.users",
                        method: "review_user_count",
                        kwargs: {
                            context: session.user_context,
                        },
                    },
                    {shadow: true}
                )
                .then(function (data) {
                    self.reviews = data;
                    self.reviewCounter = _.reduce(
                        data,
                        function (total_count, p_data) {
                            return total_count + p_data.pending_count;
                        },
                        0
                    );
                    self.$(".o_notification_counter").text(self.reviewCounter);
                    self.$el.toggleClass("o_no_notification", !self.reviewCounter);
                });
        },

        /**
         * Get particular model view to redirect on click of review on that model.
         * @private
         * @param {String} model
         * @returns {integer}
         */
        _getReviewModelViewID: function (model) {
            return this._rpc({
                model: model,
                method: "get_activity_view_id",
            });
        },

        /**
         * Update(render) activity system tray view on activity updation.
         * @private
         */
        _updateReviewPreview: function () {
            var self = this;
            self._getReviewData().then(function () {
                self.$reviews_preview.html(
                    QWeb.render("tier.validation.ReviewMenuPreview", {
                        reviews: self.reviews,
                    })
                );
            });
        },

        // ------------------------------------------------------------
        // Handlers
        // ------------------------------------------------------------

        /**
         * Redirect to specific action given its xml id
         * @private
         * @param {MouseEvent} ev
         */
        _onReviewActionClick: function (ev) {
            ev.stopPropagation();
            var actionXmlid = $(ev.currentTarget).data("action_xmlid");
            this.do_action(actionXmlid);
        },

        /**
         * Redirect to particular model view
         * @private
         * @param {MouseEvent} event
         */
        _onReviewFilterClick: function (event) {
            // Fetch the data from the button otherwise fetch the ones from the
            // parent (.o_tier_channel_preview).
            var data = _.extend(
                {},
                $(event.currentTarget).data(),
                $(event.target).data()
            );
            var context = {};
            var domain = [["can_review", "=", true]];
            console.log(data);
            if (data.active_field) {
                domain.push(["active", "in", [true, false]]);
            }
            this.do_action({
                type: "ir.actions.act_window",
                name: data.model_name,
                res_model: data.res_model,
                views: [
                    [false, "list"],
                    [false, "form"],
                ],
                search_view_id: [false],
                domain: domain,
                context: context,
            });
        },

        /**
         * When menu clicked update activity preview if counter updated
         * @private
         * @param {MouseEvent} event
         */
        _onReviewMenuShow: function () {
            this._updateReviewPreview();
        },
    });

    SystrayMenu.Items.push(ReviewMenu);

    return ReviewMenu;
});
