/* @odoo-module */
/* Copyright 2024 Tecnativa - Carlos Roca
 * License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl). */
import {AnnouncementDialog} from "@announcement/js/announcement_dialog/announcement_dialog.esm";

AnnouncementDialog.template = "announcement_dialog_size.AnnouncementDialog";
AnnouncementDialog.props = {
    ...AnnouncementDialog.props,
    size: {type: String, optional: true},
};
