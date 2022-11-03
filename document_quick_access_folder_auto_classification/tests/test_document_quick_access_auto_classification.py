# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import os
from odoo import tools
from odoo.tools import mute_logger
from odoo.tests.common import TransactionCase
from tempfile import TemporaryDirectory
from mock import patch


class Encoded:
    def __init__(self, data):
        self.data = data


class TestDocumentQuickAccessClassification(TransactionCase):

    def setUp(self):
        super().setUp()
        self.tmpdir = TemporaryDirectory()
        self.ok_tmpdir = TemporaryDirectory()
        self.no_ok_tmpdir = TemporaryDirectory()
        self.env['ir.config_parameter'].set_param(
            'document_quick_access_auto_classification.path',
            self.tmpdir.name
        )
        self.env['ir.config_parameter'].set_param(
            'document_quick_access_auto_classification.ok_path',
            self.ok_tmpdir.name
        )
        self.env['ir.config_parameter'].set_param(
            'document_quick_access_auto_classification.failure_path',
            self.no_ok_tmpdir.name
        )
        self.model_id = self.env.ref('base.model_res_partner')

    def tearDown(self):
        super().tearDown()
        self.tmpdir.cleanup()
        self.ok_tmpdir.cleanup()
        self.no_ok_tmpdir.cleanup()

    def test_ok_pdf_multi(self):
        partners = self.env['res.partner'].create({
            'name': 'Partner 1',
        })
        partners |= self.env['res.partner'].create({
            'name': 'Partner 2',
        })
        partners |= self.env['res.partner'].create({
            'name': 'Partner 3',
        })
        partners |= self.env['res.partner'].create({
            'name': 'Partner 4',
        })
        self.test_ok_pdf(partners)

    def test_ok_pdf_multi_limit(self):
        """Limit the number of files to process"""
        partner = self.env['res.partner'].create({
            'name': 'Partner 1',
        })
        self.env['document.quick.access.rule'].create({
            'model_id': self.model_id.id,
            'name': 'PARTNER',
            'priority': 1,
            'barcode_format': 'standard',
        })
        file = tools.file_open(
            'test_file.pdf',
            mode="rb",
            subdir="addons/document_quick_access_folder_auto_classification"
                   "/tests"
        ).read()
        self.env['document.quick.access.rule'].create({
            'model_id': self.model_id.id,
            'name': 'PARTNER',
            'priority': 1,
            'barcode_format': 'standard',
        })
        with open(os.path.join(self.tmpdir.name, 'test_file.pdf'), 'wb') as f:
            f.write(file)
        with open(os.path.join(
            self.tmpdir.name, 'test_file_2.pdf'
        ), 'wb') as f:
            f.write(file)
        code = [Encoded(partner.get_quick_access_code().encode("utf-8"))]
        files = os.listdir(self.tmpdir.name)
        self.assertEqual(2, len(files))
        with patch(
                'odoo.addons.document_quick_access_folder_auto_classification.'
                'models.ir_attachment.decode'
        ) as ptch:
            ptch.return_value = code
            self.env['document.quick.access.rule'].with_context(
                ignore_process_path=True
            ).cron_folder_auto_classification(limit=1)
            ptch.assert_called_once()
        attachments = self.env['ir.attachment'].search([
            ('res_model', '=', partner._name),
            ('res_id', '=', partner.id)
        ])
        self.assertTrue(attachments)
        self.assertEqual(1, len(attachments))
        files = os.listdir(self.tmpdir.name)
        self.assertEqual(1, len(files))

    def test_ok_pdf(self, partners=False):
        """Assign automatically PDFs to their assigned place"""
        if not partners:
            partners = self.env['res.partner'].create({
                'name': 'Partner',
            })
        file = tools.file_open(
            'test_file.pdf',
            mode="rb",
            subdir="addons/document_quick_access_folder_auto_classification"
                   "/tests"
        ).read()

        self.env['document.quick.access.rule'].create({
            'model_id': self.model_id.id,
            'name': 'PARTNER',
            'priority': 1,
            'barcode_format': 'standard',
        })
        with open(os.path.join(self.tmpdir.name, 'test_file.pdf'), 'wb') as f:
            f.write(file)
        code = [
            Encoded(partner.get_quick_access_code().encode('utf-8'))
            for partner in partners
        ]
        with patch(
            'odoo.addons.document_quick_access_folder_auto_classification.'
            'models.ir_attachment.decode'
        ) as ptch:
            ptch.return_value = code
            self.env['document.quick.access.rule'].with_context(
                ignore_process_path=True
            ).cron_folder_auto_classification()
            ptch.assert_called()
        self.assertTrue(partners)
        for partner in partners:
            self.assertTrue(self.env['ir.attachment'].search([
                ('res_model', '=', partner._name),
                ('res_id', '=', partner.id)
            ]))
        self.assertTrue(os.path.exists(
            os.path.join(self.ok_tmpdir.name, 'test_file.pdf')))

    def test_no_ok_assign(self):
        """Assign failed files"""
        file = tools.file_open(
            'test_file.pdf',
            mode="rb",
            subdir="addons/document_quick_access_folder_auto_classification/"
                   "tests"
        ).read()
        with open(os.path.join(self.tmpdir.name, 'test_file.pdf'), 'wb') as f:
            f.write(file)
        self.env['document.quick.access.rule'].with_context(
            ignore_process_path=True
        ).cron_folder_auto_classification()
        self.assertTrue(os.path.exists(
            os.path.join(self.no_ok_tmpdir.name, 'test_file.pdf')))
        partner = self.env['res.partner'].create({
            'name': 'Partner',
        })
        missing = self.env['document.quick.access.missing'].search([
            ('name', '=', 'test_file.pdf'),
            ('state', '=', 'pending')
        ])
        self.assertTrue(missing)
        action = missing.access_resource()
        self.assertFalse(action.keys())
        self.env['document.quick.access.rule'].create({
            'model_id': self.model_id.id,
            'name': 'PARTNER',
            'priority': 1,
            'barcode_format': 'standard',
        })
        wizard = self.env['document.quick.access.missing.assign'].create({
            'object_id': '%s,%s' % (partner._name, partner.id),
            'missing_document_id': missing.id,
        })
        wizard.doit()
        self.assertEqual(missing.state, 'processed')
        action = missing.access_resource()
        self.assertEqual(partner._name, action['res_model'])
        self.assertEqual(partner.id, action['res_id'])

    def test_failure(self):
        """We will check that if a major exception raises all is handled"""
        file = tools.file_open(
            'test_file.pdf',
            mode="rb",
            subdir="addons/document_quick_access_folder_auto_classification/"
                   "tests"
        ).read()
        with open(os.path.join(self.tmpdir.name, 'test_file.pdf'), 'wb') as f:
            f.write(file)
        with self.assertRaises(TypeError):
            with patch(
                'odoo.addons.document_quick_access_folder_auto_classification.'
                'models.ir_attachment.decode'
            ) as ptch:
                ptch.return_value = 1
                self.env['document.quick.access.rule'].with_context(
                    ignore_process_path=True
                ).cron_folder_auto_classification()

    def test_no_ok_reject(self):
        """We will check that we can manage and reject failed files"""
        file = tools.file_open(
            'test_file.pdf',
            mode="rb",
            subdir="addons/document_quick_access_folder_auto_classification/"
                   "tests"
        ).read()
        with open(os.path.join(self.tmpdir.name, 'test_file.pdf'), 'wb') as f:
            f.write(file)
        self.env['document.quick.access.rule'].with_context(
            ignore_process_path=True
        ).cron_folder_auto_classification()
        self.assertTrue(os.path.exists(
            os.path.join(self.no_ok_tmpdir.name, 'test_file.pdf')))
        missing = self.env['document.quick.access.missing'].search([
            ('name', '=', 'test_file.pdf'),
            ('state', '=', 'pending')
        ])
        self.assertTrue(missing)
        missing.reject_assign_document()
        self.assertEqual(missing.state, 'deleted')

    def test_corrupted(self):
        """We will check that corrupted files are removed"""
        file = tools.file_open(
            'test_file.pdf',
            mode="rb",
            subdir="addons/document_quick_access_folder_auto_classification/"
                   "tests"
        ).read()
        with open(os.path.join(self.tmpdir.name, 'test_file.pdf'), 'wb') as f:
            f.write(file[:int(len(file)/2)])
        with mute_logger(
            'odoo.addons.document_quick_access_folder_auto_classification.'
            'models.document_quick_access_rule',
            'odoo.addons.document_quick_access_folder_auto_classification.'
            'models.ir_attachment'
        ):
            self.env['document.quick.access.rule'].with_context(
                ignore_process_path=True
            ).cron_folder_auto_classification()
        self.assertFalse(
            os.path.exists(os.path.join(self.ok_tmpdir.name, 'test_file.pdf'))
        )
        self.assertFalse(os.path.exists(
            os.path.join(self.no_ok_tmpdir.name, 'test_file.pdf')))
        self.assertFalse(
            os.path.exists(os.path.join(self.tmpdir.name, 'test_file.pdf'))
        )
