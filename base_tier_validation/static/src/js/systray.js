odoo.define('tier_validation.systray', function (require) {
    "use strict";

    var config = require('web.config');
    var core = require('web.core');
    var session = require('web.session');
    var SystrayMenu = require('web.SystrayMenu');
    var Widget = require('web.Widget');
    var bus = require('bus.bus').bus;

    var QWeb = core.qweb;

    var ReviewMenu = Widget.extend({
        template:'tier.validation.ReviewMenu',
        events: {
            "click": "_onReviewMenuClick",
            "click .o_mail_channel_preview": "_onReviewFilterClick",
        },
        start: function () {
            this.$reviews_preview = this.$('.o_mail_navbar_dropdown_channels');
            this._updateReviewPreview();
            this.channel = 'base.tier.validation';
            bus.add_channel(this.channel);
            bus.on('notification', this, this.bus_notification);
            return this._super();
        },

        bus_notification: function(notifications) {
            var self = this;
            _.each(notifications, function (notification) {
                var channel = notification[0];
                if (channel === self.channel) {
                    self._updateReviewPreview();
                }
            });
        },
        // Private

        /**
         * Make RPC and get current user's activity details
         * @private
         */
        _getReviewData: function(){
            var self = this;

            return self._rpc({
                model: 'res.users',
                method: 'review_user_count',
                kwargs: {
                    context: session.user_context,
                },
            }).then(function (data) {
                self.reviews = data;
                self.reviewCounter = _.reduce(data, function(total_count, p_data){ return total_count + p_data.pending_count; }, 0);
                self.$('.o_notification_counter').text(self.reviewCounter);
                self.$el.toggleClass('o_no_notification', !self.reviewCounter);
            });
        },
        /**
         * Check wether activity systray dropdown is open or not
         * @private
         * @returns {boolean}
         */
        _isOpen: function () {
            return this.$el.hasClass('open');
        },
        /**
         * Update(render) activity system tray view on activity updation.
         * @private
         */
        _updateReviewPreview: function () {
            var self = this;
            self._getReviewData().then(function (){
                self.$reviews_preview.html(QWeb.render('tier.validation.ReviewMenuPreview', {
                    reviews : self.reviews
                }));
            });
        },
        /**
         * update counter based on activity status(created or Done)
         * @private
         * @param {Object} [data] key, value to decide activity created or deleted
         * @param {String} [data.type] notification type
         * @param {Boolean} [data.activity_deleted] when activity deleted
         * @param {Boolean} [data.activity_created] when activity created
         */
        _updateCounter: function (data) {
            if (data) {
                if (data.review_created) {
                    this.reviewCounter ++;
                }
                if (data.review_deleted && this.reviewCounter > 0) {
                    this.reviewCounter --;
                }
                this.$('.o_notification_counter').text(this.reviewCounter);
                this.$el.toggleClass('o_no_notification', !this.reviewCounter);
            }
        },


        // Handlers

        /**
         * Redirect to particular model view
         * @private
         * @param {MouseEvent} event
         */
        _onReviewFilterClick: function (event) {
            // fetch the data from the button otherwise fetch the ones from the parent (.o_tier_channel_preview).
            var data = _.extend({}, $(event.currentTarget).data(), $(event.target).data());
            var context = {};
            this.do_action({
                type: 'ir.actions.act_window',
                name: data.model_name,
                res_model:  data.res_model,
                views: [[false, 'list'], [false, 'form']],
                search_view_id: [false],
                domain: [['review_ids.reviewer_ids', '=', session.uid],
                ['review_ids.status', '=', 'pending']],
                context:context,
            });
        },
        /**
         * When menu clicked update activity preview if counter updated
         * @private
         * @param {MouseEvent} event
         */
        _onReviewMenuClick: function () {
            if (!this._isOpen()) {
                this._updateReviewPreview();
            }
        },

    });

    SystrayMenu.Items.push(ReviewMenu);

    // to test activity menu in qunit test cases we need it
    return {
        ReviewMenu: ReviewMenu,
    };
});