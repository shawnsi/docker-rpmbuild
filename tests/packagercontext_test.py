from mock import mock_open, patch, DEFAULT, MagicMock
import unittest

from rpmbuild import PackagerContext, PackagerException


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

    def test_image_throws_packagerexception_if_empty(self):
        self.assertRaises(PackagerException, PackagerContext, image=None)

    def test_defines_is_empty_list_if_not_provided(self):
        self.assertEqual(PackagerContext(image='foo').defines, [])

    def test_sources_is_empty_list_if_not_provided(self):
        self.assertEqual(PackagerContext(image='foo').sources, [])

    def test_sources_dir_is_set_if_path_exists(self):
        self.file = '/root/magicfile.txt'
        with patch('os.path.exists') as exists_mock:
            exists_mock.return_value = True
            self.assertEqual(
                PackagerContext(image='foo', sources_dir=self.file).sources_dir,
                self.file,
                'Sources dir should exists if os.path.exists says it does exists.')

    def test_sources_dir_is_none_if_path_does_not_exists(self):
        self.file = '/root/magicfile.txt'
        with patch('os.path.exists') as exists_mock:
            exists_mock.return_value = False
            self.assert_(PackagerContext(image='foo', sources_dir=self.file).sources_dir is None,
                              'Sources dir should not be set when os.path.exists says it does not')
