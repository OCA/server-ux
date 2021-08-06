odoo.define("base_tier_validation.ReviewField", function (require) {
    "use strict";

    var AbstractField = require("web.AbstractField");
    var core = require("web.core");
    var field_registry = require("web.field_registry");
    var rpc = require("web.rpc");
    var QWeb = core.qweb;

    $(document).on({
        ajaxStart: function () {
            var res_ids = window.self_arr;
            if (res_ids) {
                rpc.query({
                    model: "res.users",
                    method: "get_reviews",
                    args: [res_ids],
                }).then(function (data) {
                    self.reviews = data;
                    if (data && data.length > 0) {
                        for (var i = 0; i < data.length; i++) {
                            if (data[i].status == "pending") {
                                var tier_review_msg =
                                    "<p class='review_description'>(" +
                                    data[i].name +
                                    ")</p>";

                                var validate_tier_btn = $('button[name="reject_tier"]');
                                var review_msg_elems = $(".review_description");
                                try {
                                    for (var i = 0; i < review_msg_elems.length; i++) {
                                        review_msg_elems[i].remove();
                                    }
                                    $(tier_review_msg).insertAfter(validate_tier_btn);
                                } catch (error) {}

                                break;
                            }
                        }
                    }
                });
            }
        },
    });

    var ReviewField = AbstractField.extend({
        template: "tier.review.Collapse",
        events: {
            "click .o_info_btn": "_onButtonClicked",
            "show.bs.collapse": "_showCollapse",
            "hide.bs.collapse": "_hideCollapse",
        },
        start: function () {
            var self = this;
            try {
                window.self_arr = self.value;
            } catch (error) {}
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
                model: "res.users",
                method: "get_reviews",
                args: [res_ids],
            }).then(function (data) {
                self.reviews = data;
            });
        },
        _renderDropdown: function () {
            var self = this;
            return this._getReviewData(self.value).then(function () {
                self.$(".o_review").html(
                    QWeb.render("tier.review.ReviewsTable", {
                        reviews: self.reviews,
                    })
                );
            });
        },
        _onButtonClicked: function (event) {
            event.preventDefault();
            if (!this.$el.hasClass("open")) {
                this._renderDropdown();
            }
        },
        _showCollapse: function () {
            this.$el.find(".panel-heading").addClass("active");
        },
        _hideCollapse: function () {
            this.$el.find(".panel-heading").removeClass("active");
        },
    });

    field_registry.add("tier_validation", ReviewField);

    return ReviewField;
});
