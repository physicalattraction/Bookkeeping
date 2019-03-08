from django.test import TestCase

from common.utils import extract_name_from_full_path_to_file


class ExtractNameFromFullPathToFileTestCase(TestCase):
    def test_that_base_name_is_extracted_with_path_with_extension(self):
        full_path_to_file = 'aaa.bbb.ccc/ddd.eee.fff/ggg.hhh.iii'
        self.assertEqual('ggg.hhh', extract_name_from_full_path_to_file(full_path_to_file))

    def test_that_base_name_is_extracted_without_path_with_extension(self):
        full_path_to_file = 'ggg.hhh.iii'
        self.assertEqual('ggg.hhh', extract_name_from_full_path_to_file(full_path_to_file))

    def test_that_base_name_is_extracted_with_path_without_extension(self):
        full_path_to_file = 'aaa.bbb.ccc/ddd.eee.fff/ggg'
        self.assertEqual('ggg', extract_name_from_full_path_to_file(full_path_to_file))

    def test_that_base_name_is_extracted_without_path_without_extension(self):
        full_path_to_file = 'ggg'
        self.assertEqual('ggg', extract_name_from_full_path_to_file(full_path_to_file))
