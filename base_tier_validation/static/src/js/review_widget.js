odoo.define('base_tier_validation.ReviewField', function (require) {
    "use strict";

    var AbstractField = require('web.AbstractField');
    var core = require('web.core');
    var session = require('web.session');
    var field_registry = require('web.field_registry');
    var Widget = require('web.Widget');

    var _t = core._t;
    var QWeb = core.qweb;

    var ReviewField = AbstractField.extend({
        template: 'tier.review.ReviewPopUp',
        events: {
            'click .o_info_btn': '_onButtonClicked',
        },
        start: function () {
            var self = this;
            console.log(self)

        },
        /**
         * Make RPC and get current user's activity details
         * @private
         */
        _getReviewData: function(res_ids){
            var self = this;

            return self._rpc({
                model: 'res.users',
                method: 'get_reviews',
                args: [res_ids],
            }).then(function (data) {
                self.reviews = data;
            });
        },
        _renderDropdown: function () {
            var self = this;
            return this._getReviewData(self.value).then(function (){
                self.$('.o_review').html(QWeb.render("tier.review.ReviewDropDown", {
                    reviews : self.reviews
                }));
            });
        },
        _onButtonClicked: function (event) {
            event.preventDefault();
            if (!this.$el.hasClass('open')) {
                this._renderDropdown();
            }
        },
    });

    field_registry.add('review_popup', ReviewField);

    return ReviewField;

    });
