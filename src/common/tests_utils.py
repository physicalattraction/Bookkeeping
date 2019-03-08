from django.test import TestCase

from common.utils import concatenate_matrices, extract_name_from_full_path_to_file


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


class ConcatenateMatricesTestCase(TestCase):
    def test_that_two_matrices_are_merged_with_left_matrix_larger(self):
        left = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        right = [['A', 'B'], ['C', 'D']]
        concatenated_matrix = [[1, 2, 3, 'A', 'B'], [4, 5, 6, 'C', 'D'], [7, 8, 9, None, None]]
        self.assertListEqual(concatenated_matrix, concatenate_matrices(left, right))

    def test_that_two_matrices_are_merged_with_right_matrix_larger(self):
        left = [[1, 2, 3], [4, 5, 6]]
        right = [['A', 'B'], ['C', 'D'], ['E', 'F']]
        concatenated_matrix = [[1, 2, 3, 'A', 'B'], [4, 5, 6, 'C', 'D'], [None, None, None, 'E', 'F']]
        self.assertListEqual(concatenated_matrix, concatenate_matrices(left, right))
