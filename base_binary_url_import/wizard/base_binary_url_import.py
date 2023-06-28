# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
import base64
import json
import logging
from collections import Counter

import pyrfc6266
import requests
from requests.exceptions import HTTPError

from odoo import _, api, fields, models
from odoo.exceptions import AccessError, UserError

DEFAULT_BINARY_CHUNK_SIZE = 32768
DEFAULT_BINARY_IMPORT_TIMEOUT = 5
DEFAULT_BINARY_IMPORT_MAXBYTES = 10 * 1024 * 1024
LINE_BREAK_CHAR = "\n"
SEPARATOR_CHAR = ","


_logger = logging.getLogger(__name__)


class BaseBinaryURLImport(models.TransientModel):

    _name = "base.binary.url.import"
    _description = "Import of binaries from URL wizard"

    target_model_id = fields.Many2one(
        "ir.model", domain=[("transient", "=", False)], required=True
    )
    target_binary_field_id = fields.Many2one("ir.model.fields", required=True)
    target_binary_field_domain = fields.Char(
        compute="_compute_allowed_target_fields_domain"
    )
    target_binary_filename_field_id = fields.Many2one("ir.model.fields")
    target_binary_filename_field_domain = fields.Char(
        compute="_compute_allowed_target_fields_domain"
    )

    line_ids = fields.One2many("base.binary.url.import.line", "wizard_id")

    @api.model
    def check_access_rights(self, operation, raise_exception=True):
        res = super().check_access_rights(operation, raise_exception=raise_exception)
        if not self.env.user._can_import_remote_urls():
            raise AccessError(
                _(
                    "You can not import files via URL, check with your "
                    "administrator for the reason."
                )
            )
        return res

    def _get_ir_model_fields_domain(self, ttype):
        self.ensure_one()
        return [("ttype", "=", ttype), ("model_id", "=", self.target_model_id.id)]

    @api.depends("target_model_id")
    def _compute_allowed_target_fields_domain(self):
        for wiz in self:
            binary_domain = wiz._get_ir_model_fields_domain("binary")
            char_domain = wiz._get_ir_model_fields_domain("char")
            wiz.target_binary_field_domain = json.dumps(binary_domain)
            wiz.target_binary_filename_field_domain = json.dumps(char_domain)

    @api.onchange("line_ids")
    def onchange_line_ids(self):
        for wiz_line in self.line_ids:
            if LINE_BREAK_CHAR in (wiz_line.binary_url_to_import or ""):
                split_lines = wiz_line.binary_url_to_import.split(LINE_BREAK_CHAR)
                split_lines = list(filter(None, split_lines))
                if SEPARATOR_CHAR in split_lines[0]:
                    line_identifier, url = split_lines[0].split(SEPARATOR_CHAR)
                    wiz_line.update(self._prepare_wiz_line_vals(line_identifier, url))
                wiz_lines_commands = self._generate_wiz_lines_commands(split_lines[1:])
                self.update({"line_ids": wiz_lines_commands})
                break

        if self.line_ids:
            self.lines_sanity_check()

    def _generate_wiz_lines_commands(self, split_lines):
        commands = []
        for line in split_lines:
            line_identifier, url = line.split(SEPARATOR_CHAR)
            line_vals = self._prepare_wiz_line_vals(line_identifier, url)
            commands.append((0, 0, line_vals))
        return commands

    def _prepare_wiz_line_vals(self, identifier, url):
        return {
            "target_record_identifier": identifier,
            "binary_url_to_import": url,
        }

    def _get_db_and_xml_ids(self):
        db_ids = []
        xml_ids = []
        # Check target IDs are integers or XMLIDs
        for wiz_line in self.line_ids:
            id_type = wiz_line._get_identifier_type()
            if id_type == "db_id":
                db_ids.append(int(wiz_line.target_record_identifier))
            elif id_type == "xml_id":
                xml_ids.append(wiz_line.target_record_identifier)
        return db_ids, xml_ids

    def _check_db_ids_exist(self, db_ids):
        db_ids_records = self.env[self.target_model_id.model].browse(db_ids).exists()
        unexisting_ids = set(db_ids) - set(db_ids_records.ids)
        if unexisting_ids:
            raise UserError(
                _("Following IDs do not exist in database:\n %s")
                % LINE_BREAK_CHAR.join([str(db_id) for db_id in unexisting_ids])
            )

    def _check_db_ids_duplicated(self, db_ids):
        db_ids_set = set(db_ids)
        if len(db_ids_set) != len(db_ids):
            db_ids_counter = Counter(db_ids)
            duplicated_db_ids = [
                db_id for db_id in db_ids_counter.keys() if db_ids_counter[db_id] > 1
            ]
            raise UserError(
                _("Same database IDs are duplicated:\n %s")
                % LINE_BREAK_CHAR.join([str(db_id) for db_id in duplicated_db_ids])
            )

    def _check_xml_ids_exist(self, xml_ids):
        unexisting_xml_ids = []
        for xml_id in xml_ids:
            xml_id_rec = self.env.ref(xml_id, raise_if_not_found=False)
            if xml_id_rec is None:
                unexisting_xml_ids.append(xml_id)
            elif xml_id_rec._name != self.target_model_id.model:
                raise UserError(
                    _(
                        "XML ID %(xml_id)s matches a record of model "
                        "%(model_name)s instead of model %(tagert_model_name)s"
                    )
                    % {
                        "xml_id": xml_id,
                        "model_name": xml_id_rec._name,
                        "tagert_model_name": self.target_model_id._name,
                    }
                )
        if unexisting_xml_ids:
            raise UserError(
                _("Following XML IDs do not exist in database:\n %s")
                % LINE_BREAK_CHAR.join(unexisting_xml_ids)
            )

    def _check_xml_ids_duplicated(self, xml_ids):
        xml_ids_set = set(xml_ids)
        if len(xml_ids_set) != len(xml_ids):
            xml_ids_counter = Counter(xml_ids)
            duplicated_xml_ids = [
                xml_id
                for xml_id in xml_ids_counter.keys()
                if xml_ids_counter[xml_id] > 1
            ]
            raise UserError(
                _("Same XML IDs are duplicated:\n %s")
                % LINE_BREAK_CHAR.join(duplicated_xml_ids)
            )

    def _check_db_ids_xml_ids_intersecting(self, db_ids, xml_ids):
        xml_ids_records_ids_map = {
            xml_id: self.env.ref(xml_id, raise_if_not_found=False).id
            for xml_id in xml_ids
        }
        db_ids_set = set(db_ids)
        xml_ids_db_ids_set = set(xml_ids_records_ids_map.values())
        intersects = db_ids_set.intersection(xml_ids_db_ids_set)
        if intersects:
            raise UserError(
                _("Following DB IDs intersect with XML IDs:\n %s")
                % LINE_BREAK_CHAR.join([str(db_id) for db_id in intersects])
            )

    def lines_sanity_check(self):
        """Check if IDs are existing for selected model and we don't have two
        lines matching same record"""
        self.ensure_one()
        db_ids, xml_ids = self._get_db_and_xml_ids()
        # Check DB IDs exist
        self._check_db_ids_exist(db_ids)
        # Check we don't have two lines targeting same DB ID
        self._check_db_ids_duplicated(db_ids)
        # Check XML IDs exist and match target model
        self._check_xml_ids_exist(xml_ids)
        # Check we don't have two lines targeting same XML ID
        self._check_xml_ids_duplicated(xml_ids)
        # Check no intersection between XML IDs and DB IDs
        self._check_db_ids_xml_ids_intersecting(db_ids, xml_ids)

    def action_import_lines(self):
        self.ensure_one()
        self.lines_sanity_check()
        updated_ids = []
        with requests.Session() as session:
            for line in self.line_ids:
                updated_ids.append(line.import_binary_from_url(session))
        domain = [("id", "in", updated_ids)]
        return {
            "name": _("Updated records"),
            "type": "ir.actions.act_window",
            "res_model": self.target_model_id.model,
            "domain": domain,
            "view_mode": "tree,form",
        }


class BaseBinaryURLImportLine(models.TransientModel):

    _name = "base.binary.url.import.line"
    _description = "Import of binaries from URL wizard line"

    wizard_id = fields.Many2one("base.binary.url.import", required=True)
    target_record_identifier = fields.Char(string="Target record ID")
    is_target_record_identifier_required = fields.Boolean(
        compute="_compute_is_target_record_identifier_required"
    )
    binary_url_to_import = fields.Char(string="URL to import", required=True)

    @api.depends("binary_url_to_import")
    def _compute_is_target_record_identifier_required(self):
        for line in self:
            line.is_target_record_identifier_required = (
                SEPARATOR_CHAR not in line.binary_url_to_import
                if line.binary_url_to_import
                else False
            )

    def _get_identifier_type(self):
        self.ensure_one()
        target_id = self.target_record_identifier
        if not target_id:
            return
        if target_id.isdigit():
            return "db_id"
        elif "." in target_id:
            return "xml_id"
        else:
            raise UserError(_("Identifier %s is not an Integer or XMLID") % target_id)

    def _get_target_record(self):
        self.ensure_one()
        rec = None
        if self._get_identifier_type() == "db_id":
            rec = self.env[self.wizard_id.target_model_id.model].browse(
                int(self.target_record_identifier)
            )
        elif self._get_identifier_type() == "xml_id":
            rec = self.env.ref(self.target_record_identifier)
        return rec

    def import_binary_from_url(self, request_session=None):
        self.ensure_one()
        if request_session is None:
            request_session = requests
        binary_content, filename = self._import_content_from_url(request_session)
        target_record = self._get_target_record()
        vals = {
            self.wizard_id.target_binary_field_id.name: base64.b64encode(binary_content)
        }
        if self.wizard_id.target_binary_filename_field_id:
            vals.update(
                {
                    self.wizard_id.target_binary_filename_field_id.name: filename,
                }
            )
        target_record.write(vals)
        return target_record.id

    def _import_content_from_url(self, request_session):
        # Adapted from base_import module
        maxsize = (
            int(
                self.env["ir.config_parameter"].get_param("binary.url.import.max.size")
                or "0"
            )
            or DEFAULT_BINARY_IMPORT_MAXBYTES
        )
        timeout = (
            int(
                self.env["ir.config_parameter"].get_param("binary.url.import.timeout")
                or "0"
            )
            or DEFAULT_BINARY_IMPORT_TIMEOUT
        )
        _logger.debug(
            "Trying to import Binary from URL: %s " % self.binary_url_to_import
        )
        except_message = ""
        try:
            with request_session.get(
                self.binary_url_to_import, timeout=timeout, stream=True
            ) as response:
                response.raise_for_status()

                if (
                    response.headers.get("Content-Length")
                    and int(response.headers["Content-Length"]) > maxsize
                ):
                    raise ValueError(
                        _("File size exceeds configured maximum (%s bytes)") % maxsize
                    )

                content = bytearray()
                for chunk in response.iter_content(DEFAULT_BINARY_CHUNK_SIZE):
                    content += chunk
                    if len(content) > maxsize:
                        raise ValueError(
                            _("File size exceeds configured maximum (%s bytes)")
                            % maxsize
                        )
                # Use pyrfc6266 to get the filename from
                # Content-Disposition in the HTTP response header
                filename = pyrfc6266.requests_response_to_filename(response)

        except HTTPError as e:
            _logger.exception(e)
            except_message = e
        if except_message:
            raise UserError(
                _("Could not retrieve URL: %(url)s : %(error)s")
                % {"url": self.binary_url_to_import, "error": except_message}
            )

        return content, filename
