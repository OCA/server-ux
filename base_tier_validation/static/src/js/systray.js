odoo.define("tier_validation.systray", function(require) {
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
        start: function() {
            this.$reviews_preview = this.$(".o_mail_systray_dropdown_items");
            this._updateReviewPreview();
            var channel = "base.tier.validation";
            this.call("bus_service", "addChannel", channel);
            this.call("bus_service", "startPolling");
            this.call("bus_service", "onNotification", this, this._updateReviewPreview);
            return this._super();
        },

        // Private

        /**
         * Make RPC and get current user's activity details
         * @private
         * @returns {integer}
         */
        _getReviewData: function() {
            var self = this;

            return self
                ._rpc({
                    model: "res.users",
                    method: "review_user_count",
                    kwargs: {
                        context: session.user_context,
                    },
                })
                .then(function(data) {
                    self.reviews = data;
                    self.reviewCounter = _.reduce(
                        data,
                        function(total_count, p_data) {
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
        _getReviewModelViewID: function(model) {
            return this._rpc({
                model: model,
                method: "get_activity_view_id",
            });
        },

        /**
         * Update(render) activity system tray view on activity updation.
         * @private
         */
        _updateReviewPreview: function() {
            var self = this;
            self._getReviewData().then(function() {
                self.$reviews_preview.html(
                    QWeb.render("tier.validation.ReviewMenuPreview", {
                        reviews: self.reviews,
                    })
                );
            });
        },

        /**
         * Update counter based on activity status(created or Done)
         * @private
         * @param {Object} [data] key, value to decide activity created or deleted
         * @param {String} [data.type] notification type
         * @param {Boolean} [data.activity_deleted] when activity deleted
         * @param {Boolean} [data.activity_created] when activity created
         */
        _updateCounter: function(data) {
            if (data) {
                if (data.review_created) {
                    this.reviewCounter++;
                }
                if (data.review_deleted && this.reviewCounter > 0) {
                    this.reviewCounter--;
                }
                this.$(".o_notification_counter").text(this.reviewCounter);
                this.$el.toggleClass("o_no_notification", !this.reviewCounter);
            }
        },

        // ------------------------------------------------------------
        // Handlers
        // ------------------------------------------------------------

        /**
         * Redirect to specific action given its xml id
         * @private
         * @param {MouseEvent} ev
         */
        _onReviewActionClick: function(ev) {
            ev.stopPropagation();
            var actionXmlid = $(ev.currentTarget).data("action_xmlid");
            this.do_action(actionXmlid);
        },

        /**
         * Redirect to particular model view
         * @private
         * @param {MouseEvent} event
         */
        _onReviewFilterClick: function(event) {
            // Fetch the data from the button otherwise fetch the ones from the
            // parent (.o_tier_channel_preview).
            var data = _.extend(
                {},
                $(event.currentTarget).data(),
                $(event.target).data()
            );
            var context = {};
            this.do_action({
                type: "ir.actions.act_window",
                name: data.model_name,
                res_model: data.res_model,
                views: [
                    [false, "list"],
                    [false, "form"],
                ],
                search_view_id: [false],
                domain: [
                    ["review_ids.reviewer_ids", "=", session.uid],
                    ["review_ids.status", "=", "pending"],
                    ["review_ids.can_review", "=", true],
                ],
                context: context,
            });
        },

        /**
         * When menu clicked update activity preview if counter updated
         * @private
         * @param {MouseEvent} event
         */
        _onReviewMenuShow: function() {
            this._updateReviewPreview();
        },
    });

    SystrayMenu.Items.push(ReviewMenu);

    return ReviewMenu;
});
