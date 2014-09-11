from mock import mock_open, patch, DEFAULT, MagicMock
import unittest

from rpmbuild import PackagerContext


class PackagerContextTestCase(unittest.TestCase):
    """Tests for __init__.py"""

    def setUp(self):
        self.context_defaults = dict(
                image=None,
                defines=[],
                macrofiles=[],
                sources=[],
                sources_dir=None,
                spec=None,
                retrieve=None,
                srpm=None)
        self.open = mock_open()

    def test_packager_context_str(self):
        context = PackagerContext('foo', spec='foo.spec')
        self.assertEqual(str(context), 'foo.spec')
        context = PackagerContext('foo', srpm='foo.srpm')
        self.assertEqual(str(context), 'foo.srpm')

    @patch('shutil.copy')
    @patch('tempfile.mkdtemp', return_value='/context')
    def test_packager_context_setup_macrofiles(self, mkdtemp, copy):
        with patch('rpmbuild.open', self.open, create=True):
            context = PackagerContext('foo', macrofiles=['foo.macro'])
            context.setup()
            copy.assert_called_with('foo.macro', '/context')

    @patch('shutil.copy')
    @patch('tempfile.mkdtemp', return_value='/context')
    def test_packager_context_setup_spec(self, mkdtemp, copy):
        with patch('rpmbuild.open', self.open, create=True):
            context = PackagerContext('foo', spec='foo.spec')
            context.template.render = MagicMock()
            context.setup()
            copy.assert_called_with('foo.spec', '/context')
            self.context_defaults.update(image='foo', spec='foo.spec')
            context.template.render.assert_called_with(**self.context_defaults)

    @patch('shutil.copy')
    @patch('tempfile.mkdtemp', return_value='/context')
    def test_packager_context_setup_sources(self, mkdtemp, copy):
        with patch('rpmbuild.open', self.open, create=True):
            context = PackagerContext('foo', sources=['foo.tar.gz'])
            context.setup()
            copy.assert_called_with('foo.tar.gz', '/context')

    @patch.multiple('shutil', copy=DEFAULT, copytree=DEFAULT)
    @patch('tempfile.mkdtemp', return_value='/context')
    def test_packager_context_setup_spec_sources_dir(self, mkdtemp, copy, copytree):
        with patch('rpmbuild.open', self.open, create=True):
            context = PackagerContext('foo', spec='foo.spec', sources_dir='/tmp')
            context.setup()
            copy.assert_called_with('foo.spec', '/context')
            copytree.assert_called_with('/tmp', '/context/SOURCES')

    @patch('shutil.copy')
    @patch('tempfile.mkdtemp', return_value='/context')
    def test_packager_context_setup_srpm(self, mkdtemp, copy):
        with patch('rpmbuild.open', self.open, create=True):
            context = PackagerContext('foo', srpm='foo.srpm')
            context.setup()
            copy.assert_called_with('foo.srpm', '/context')

    @patch.multiple('shutil', copy=DEFAULT, rmtree=DEFAULT)
    @patch('tempfile.mkdtemp', return_value='/context')
    def test_packager_context_teardown(self, mkdtemp, copy, rmtree):
        with patch('rpmbuild.open', self.open, create=True):
            context = PackagerContext('foo', spec='foo.spec')
            context.setup()
            context.teardown()
            rmtree.assert_called_with('/context')
