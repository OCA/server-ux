/** @odoo-module **/

import {_lt} from "@web/core/l10n/translation";
import {Dialog} from "@web/core/dialog/dialog";
import {formatDateTime, parseDateTime} from "@web/core/l10n/dates";
import {formatMany2one} from "@web/fields/formatters";
import {registry} from "@web/core/registry";

const {hooks} = owl;
const {useState} = hooks;

const debugRegistry = registry.category("debug");

class GetMetadataDialog extends Dialog {
    setup() {
        super.setup();
        this.state = useState({});
    }

    async willStart() {
        await this.getMetadata();
    }

    async toggleNoupdate() {
        await this.env.services.orm.call("ir.model.data", "toggle_noupdate", [
            this.props.res_model,
            this.state.id,
        ]);
        await this.getMetadata();
    }

    async getMetadata() {
        const metadata = (
            await this.env.services.orm.call(this.props.res_model, "get_metadata", [
                this.props.selectedIds,
            ])
        )[0];
        this.state.id = metadata.id;
        this.state.xmlid = metadata.xmlid;
        this.state.creator = formatMany2one(metadata.create_uid);
        this.state.lastModifiedBy = formatMany2one(metadata.write_uid);
        this.state.noupdate = metadata.noupdate;
        this.state.create_date = formatDateTime(parseDateTime(metadata.create_date), {
            timezone: true,
        });
        this.state.write_date = formatDateTime(parseDateTime(metadata.write_date), {
            timezone: true,
        });
        this.state.archive_uid = formatMany2one(metadata.archive_uid);
        this.state.archive_date = formatDateTime(parseDateTime(metadata.archive_date), {
            timezone: true,
        });
    }
}
GetMetadataDialog.bodyTemplate = "web.DebugMenu.getMetadataBody";
GetMetadataDialog.title = _lt("View Metadata");

function viewMetadata({action, component, env}) {
    const selectedIds = component.widget.getSelectedIds();
    if (selectedIds.length !== 1) {
        return null;
    }
    return {
        type: "item",
        description: env._t("View Metadata"),
        callback: () => {
            env.services.dialog.add(GetMetadataDialog, {
                res_model: action.res_model,
                selectedIds,
            });
        },
        sequence: 320,
    };
}

debugRegistry.category("form").remove("viewMetadata");
debugRegistry.category("form").add("viewMetadata", viewMetadata);
