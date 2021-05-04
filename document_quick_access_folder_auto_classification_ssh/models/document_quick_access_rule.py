# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import os
import shutil
import stat
from odoo import api, models
from odoo.modules.registry import Registry
from odoo.addons.queue_job.job import job
import logging
_logger = logging.getLogger(__name__)

try:
    from paramiko.client import SSHClient
except (ImportError, IOError) as err:
    _logger.info(err)


class DocumentQuickAccessRule(models.Model):
    _inherit = 'document.quick.access.rule'

    @api.model
    def cron_folder_ssh_auto_classification(
        self,
        host=False,
        port=False,
        user=False,
        password=False,
        ssh_path=False,
    ):
        dest_path = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("document_quick_access_auto_classification.path",
                       default=False)
        )
        connection = SSHClient()
        connection.load_system_host_keys()
        if not dest_path:
            return False

        if not host:
            host = self.env["ir.config_parameter"].get_param(
                "document_quick_access_"
                "folder_auto_classification_ssh.host",
                default=False
            )
        if not port:
            port = int(
                self.env["ir.config_parameter"].get_param(
                    "document_quick_access_"
                    "folder_auto_classification_ssh.port",
                    default="0"
                )
            )
        if not user:
            user = self.env["ir.config_parameter"].get_param(
                "document_quick_access_"
                "folder_auto_classification_ssh.user",
                default=False
            )
        if not password:
            password = self.env["ir.config_parameter"].get_param(
                "document_quick_access_"
                "folder_auto_classification_ssh.password",
                default=False,
            )

        if not ssh_path:
            ssh_path = self.env["ir.config_parameter"].get_param(
                "document_quick_access_"
                "folder_auto_classification_ssh.path",
                default=False,
            )
        connection.connect(
            hostname=host, port=port, username=user, password=password
        )
        sftp = connection.open_sftp()
        if ssh_path:
            sftp.chdir(ssh_path)
        elements = sftp.listdir_attr(".")
        for element in elements:
            if stat.S_ISDIR(element.st_mode):
                continue
            obj = self
            new_element = element
            if not self.env.context.get('test_queue_job_no_delay', False):
                new_cr = Registry(self.env.cr.dbname).cursor()
            try:
                if not self.env.context.get('test_queue_job_no_delay', False):
                    obj = api.Environment(
                        new_cr, self.env.uid, self.env.context
                    )[self._name].browse().with_delay(**self._delay_vals())
                new_element = os.path.join(dest_path, element.filename)
                sftp.get(element.filename, new_element)
                obj._process_document(new_element)
                if not self.env.context.get('test_queue_job_no_delay', False):
                    new_cr.commit()
            except Exception:
                if os.path.exists(new_element):
                    os.unlink(new_element)
                    if not self.env.context.get(
                        'test_queue_job_no_delay', False
                    ):
                        new_cr.rollback()
                raise
            finally:
                if not self.env.context.get('test_queue_job_no_delay', False):
                    new_cr.close()
            sftp.remove(element.filename)
        sftp.close()
        connection.close()
        return True
