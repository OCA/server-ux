/* Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
   License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */
odoo.define("base_tier_validation.systray_tests", function (require) {
    "use strict";

    /* global QUnit*/

    var BusService = require("bus.BusService");
    var ReviewMenu = require("tier_validation.systray");
    var testUtils = require("web.test_utils");
    var Widget = require("web.Widget");

    var TIER_CHANNEL = "base.tier.validation";
    var PARTNER_CHANNEL = ["db", "res.partner", 3];

    /**
     * Start a review menu on the real bus service. The mock server holds each
     * longpolling request until the test answers it with `poll`. Every
     * review_user_count call is an assert step, and the RPC options it is sent
     * with are collected in `rpcOptions`.
     *
     * @param {Object} assert
     * @returns {Promise<Object>} parent, menu, rpcOptions and poll
     */
    async function createReviewMenu(assert) {
        var pollPromise = null;
        var rpcOptions = [];
        var parent = new Widget();
        await testUtils.mock.addMockEnvironment(parent, {
            data: {},
            services: {
                bus_service: BusService,
            },
            mockRPC: function (route, args) {
                if (route === "/longpolling/poll") {
                    pollPromise = testUtils.makeTestPromise();
                    return pollPromise;
                }
                if (args.method === "review_user_count") {
                    assert.step("review_user_count");
                    return Promise.resolve([]);
                }
                return this._super.apply(this, arguments);
            },
        });
        // The mock server does not receive the RPC options: read them on their
        // way to the ajax service.
        testUtils.mock.intercept(
            parent,
            "call_service",
            function (ev) {
                var data = ev.data;
                if (
                    data.service === "ajax" &&
                    data.method === "rpc" &&
                    data.args[1].method === "review_user_count"
                ) {
                    rpcOptions.push(data.args[2]);
                }
            },
            true
        );
        var menu = new ReviewMenu(parent);
        await menu.appendTo($("#qunit-fixture"));
        return {
            parent: parent,
            menu: menu,
            rpcOptions: rpcOptions,
            poll: async function (notifications) {
                pollPromise.resolve(notifications);
                await testUtils.nextTick();
            },
        };
    }

    QUnit.module("base_tier_validation", {}, function () {
        QUnit.module("ReviewMenu");

        QUnit.test(
            "an empty longpolling return does not refresh the counter",
            async function (assert) {
                assert.expect(3);
                var review = await createReviewMenu(assert);
                assert.verifySteps(["review_user_count"], "read on start");

                await review.poll([]);
                assert.verifySteps([], "no read after the empty return");

                review.parent.destroy();
            }
        );

        QUnit.test(
            "a notification on another channel does not refresh the counter",
            async function (assert) {
                assert.expect(3);
                var review = await createReviewMenu(assert);
                assert.verifySteps(["review_user_count"], "read on start");

                await review.poll([
                    {
                        id: 1,
                        channel: PARTNER_CHANNEL,
                        message: {type: "activity_updated"},
                    },
                ]);
                assert.verifySteps([], "no read after the partner notification");

                review.parent.destroy();
            }
        );

        QUnit.test(
            "a batch with review notifications refreshes the counter once",
            async function (assert) {
                assert.expect(4);
                var review = await createReviewMenu(assert);
                assert.verifySteps(["review_user_count"], "read on start");

                await review.poll([
                    {id: 1, channel: TIER_CHANNEL, message: {}},
                    {
                        id: 2,
                        channel: PARTNER_CHANNEL,
                        message: {type: "activity_updated"},
                    },
                    {id: 3, channel: TIER_CHANNEL, message: {}},
                ]);
                assert.verifySteps(["review_user_count"], "one read for the batch");

                review.parent.destroy();
            }
        );

        QUnit.test("the counter is always read with a shadow RPC", async function (
            assert
        ) {
            assert.expect(5);
            var review = await createReviewMenu(assert);
            await review.poll([{id: 1, channel: TIER_CHANNEL, message: {}}]);
            await testUtils.dom.click(review.menu.$(".dropdown-toggle"));
            assert.verifySteps(
                ["review_user_count", "review_user_count", "review_user_count"],
                "read on start, on the review notification and on opening the menu"
            );
            assert.deepEqual(
                _.pluck(review.rpcOptions, "shadow"),
                [true, true, true],
                "every read is a shadow RPC"
            );

            review.parent.destroy();
        });
    });
});
