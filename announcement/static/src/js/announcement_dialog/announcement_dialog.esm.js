/* @odoo-module */
/* Copyright 2024 Tecnativa - Carlos Roca
 * License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl). */
import {ConfirmationDialog} from "@web/core/confirmation_dialog/confirmation_dialog";

// Defined AnnouncementDialog to allow make possible changes in other modules
// like announcement_dialog_size
export class AnnouncementDialog extends ConfirmationDialog {}
