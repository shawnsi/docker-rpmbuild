import unittest
from mock import patch
from rpmbuild import PackagerContext, PackagerException


class PackagerContextTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def test_image_throws_packagerexception_if_empty(self):
        with self.assertRaises(PackagerException):
            PackagerContext(image=None)

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
            self.assertIsNone(PackagerContext(image='foo', sources_dir=self.file).sources_dir,
                              'Sources dir should not be set when os.path.exists says it does not')