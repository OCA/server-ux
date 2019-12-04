odoo.define('base_tier_validation.ReviewField', function (require) {
    "use strict";

    var AbstractField = require('web.AbstractField');
    var core = require('web.core');
    var field_registry = require('web.field_registry');

    var QWeb = core.qweb;

    var ReviewField = AbstractField.extend({
        template: 'tier.review.Collapse',
        events: {
            'click .o_info_btn': '_onButtonClicked',
            'show.bs.collapse': '_showCollapse',
            'hide.bs.collapse': '_hideCollapse',
        },
        start: function () {
            var self = this;
            self._renderDropdown();
        },

        /**
         * Make RPC and get current user's activity details
         * @private
         * @param {Object} res_ids
         * @returns {integer}
         */
        _getReviewData: function (res_ids) {
            var self = this;

            return this._rpc({
                model: 'res.users',
                method: 'get_reviews',
                args: [res_ids],
            }).then(function (data) {
                self.reviews = data;
            });
        },
        _renderDropdown: function () {
            var self = this;
            return this._getReviewData(self.value).then(function () {
                self.$('.o_review').html(QWeb.render("tier.review.ReviewsTable", {
                    reviews : self.reviews,
                }));
            });
        },
        _onButtonClicked: function (event) {
            event.preventDefault();
            if (!this.$el.hasClass('open')) {
                this._renderDropdown();
            }
        },
        _showCollapse: function () {
            this.$el.find('.panel-heading').addClass('active');
        },
        _hideCollapse: function () {
            this.$el.find('.panel-heading').removeClass('active');
        },
    });

    field_registry.add('tier_validation', ReviewField);

    return ReviewField;

});
