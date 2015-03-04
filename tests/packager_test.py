#!/usr/bin/env python
from mock import mock_open, patch, MagicMock
import unittest

from rpmbuild import Packager, PackagerException


@patch('rpmbuild.PackagerContext')
class PackagetTestCase(unittest.TestCase):

    docker_file_header = ''.join(['0' for x in range(512)])
    docker_file_content = 'foobar'

    def setUp(self):
        self.open = mock_open()
        self.docker_file = MagicMock()
        self.docker_file.read.return_value = self.docker_file_header + self.docker_file_content
        self.docker_client_patcher = patch('docker.Client')
        self.docker_client = self.docker_client_patcher.start()

    def test_packager_init(self, PackagerContext):
        context = PackagerContext.return_value
        Packager(context, {'foo': 'bar'})
        self.docker_client.assert_called_with(**{'foo': 'bar'})

    def test_packager_image_name(self, PackagerContext):
        context = PackagerContext.return_value
        context.__str__.return_value = 'foo'
        packager = Packager(context, {})
        self.assertEqual(packager.image_name, 'rpmbuild_foo')

    def test_packager_image_with_matches(self, PackagerContext):
        context = PackagerContext.return_value
        packager = Packager(context, {})
        packager.client = MagicMock()
        packager.client.images.return_value = ['foo', 'bar']
        self.assertEqual(packager.image, 'foo')

    def test_packager_image_without_matches(self, PackagerContext):
        context = PackagerContext.return_value
        packager = Packager(context, {})
        packager.client = MagicMock()
        packager.client.images.return_value = []
        with self.assertRaises(PackagerException):
            packager.image

    def test_packager_export_package(self, PackagerContext):
        context = PackagerContext.return_value
        packager = Packager(context, {})
        packager.container = {'Id': 0}
        packager.client = MagicMock()
        packager.client.copy.return_value = self.docker_file
        packager.client.diff.return_value = [
            {'Path': '/foo'},
            {'Path': '/rpmbuild/SOURCES/foo.tar.gz'},
            {'Path': '/rpmbuild/SPECS/foo.spec'},
            {'Path': '/rpmbuild/foo.rpm'},
            {'Path': '/rpmbuild/foo.src.rpm'},
        ]

        with patch('rpmbuild.open', self.open, create=True):
            packager.export_package('/tmp')

        packager.client.copy.assert_any_call(0, '/rpmbuild/foo.rpm')
        packager.client.copy.assert_any_call(0, '/rpmbuild/foo.src.rpm')
        self.open.assert_any_call('/tmp/foo.rpm', 'wb')
        self.open.assert_any_call('/tmp/foo.src.rpm', 'wb')
        exported = self.open()
        exported.write.assert_called_with(self.docker_file_content)

    def test_packager_string(self, PackagerContext):
        context = PackagerContext.return_value
        context.image = 'foo'
        packager = Packager(context, {})
        self.assertEqual(str(packager), 'foo')

    def test_packager_with_statement(self, PackagerContext):
        context = PackagerContext.return_value
        with Packager(context, {}):
            context.setup.assert_called_with()
        context.teardown.assert_called_with()

    def test_packager_build_image(self, PackagerContext):
        context = PackagerContext.return_value
        context.__str__.return_value = 'foo'
        context.path = '/tmp'
        packager = Packager(context, {})
        packager.client.build = MagicMock()
        packager.build_image()
        packager.client.build.assert_called_with('/tmp', tag='rpmbuild_foo', stream=True)

    def test_packager_build_package(self, PackagerContext):
        context = PackagerContext.return_value
        packager = Packager(context, {})
        packager.client = MagicMock()
        packager.client.images.return_value = [{'Id': 0}]
        result_container, result_logs = packager.build_package()
        container = packager.client.create_container.return_value
        packager.client.create_container.assert_called_with(0)
        packager.client.logs.assert_called_with(container, stream=True)
        packager.client.start.assert_called_with(container)
        self.assertEqual(result_container, container)

    def tearDown(self):
        self.docker_client_patcher.stop()

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
