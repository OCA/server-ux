/**
 * Copyright 2026 CIT Services
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
 */

import {ListController} from "@web/views/list/list_controller";
import {patch} from "@web/core/utils/patch";
import {getArchiveAccessPatch} from "@base_archive_manager/js/formController.esm";

patch(ListController.prototype, getArchiveAccessPatch());
