import csv
import os.path
from decimal import Decimal

from openpyxl import Workbook
from typing import Union

Numeric = Union[Decimal, float, int]
MatrixElement = Union[Numeric, str, None]
Matrix = [[MatrixElement]]


def write_csv(contents: [[str]], full_path_to_file: str) -> None:
    with open(full_path_to_file, 'w') as f:
        csv_writer = csv.writer(f)
        for line in contents:
            if line is not None:
                csv_writer.writerow(line)


# TODO: Write a wrapper around openpyxl, that represents an Excel file, including its path to file to save it
def write_xlsx(contents: [[str]], full_path_to_file: str, workbook: Workbook = None,
               worksheet_name: str = None) -> Workbook:
    if not worksheet_name:
        worksheet_name = extract_name_from_full_path_to_file(full_path_to_file)

    if not workbook:
        workbook = Workbook()
        worksheet = workbook.active
        worksheet.title = worksheet_name
    else:
        worksheet = workbook.create_sheet(worksheet_name)

    for line in contents:
        worksheet.append(line)
    workbook.save(full_path_to_file)
    return workbook


def extract_name_from_full_path_to_file(full_path_to_file: str) -> str:
    """
    Extract a sane name from a given filename

    :param full_path_to_file: Full path to a file
    :return: The base of the filename, stripped from extension and path information
    """

    filename = os.path.split(full_path_to_file)[-1]
    return os.path.splitext(filename)[0]


def concatenate_matrices(left: Matrix, right: Matrix) -> Matrix:
    """
    Put two matrices side by side

    :param left: Matrix-shaped contents
    :param right: Matrix-shaped contents
    :return: Matrix-shaped contents
    """

    # Make sure the matrices have equal amount of rows
    length_difference = len(left) - len(right)
    if length_difference > 0:
        # The left matrix is larger than the right matrix: add empty rows to the right matrix
        nr_columns = len(right[0])
        right += [[None] * nr_columns] * length_difference
    elif length_difference < 0:
        # The right matrix is larger than the left matrix: add empty rows to the left matrix
        nr_columns = len(left[0])
        left += [[None] * nr_columns] * -length_difference

    # Merge the matrices row by row
    return [left_row + right_row for left_row, right_row in zip(left, right)]
