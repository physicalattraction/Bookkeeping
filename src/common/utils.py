import csv
import os.path
from decimal import Decimal

from openpyxl import Workbook
from typing import Union

Numeric = Union[Decimal, float, int]


def write_csv(contents: [[str]], full_path_to_file: str) -> None:
    with open(full_path_to_file, 'w') as f:
        csv_writer = csv.writer(f)
        for line in contents:
            if line is not None:
                csv_writer.writerow(line)


def write_xlsx(contents: [[str]], full_path_to_file: str, worksheet_name: str = None) -> None:
    if not worksheet_name:
        worksheet_name = extract_name_from_full_path_to_file(full_path_to_file)
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = worksheet_name
    for line in contents:
        worksheet.append(line)
    workbook.save(full_path_to_file)


def extract_name_from_full_path_to_file(full_path_to_file: str) -> str:
    """
    Extract a sane name from a given filename

    :param full_path_to_file: Full path to a file
    :return: The base of the filename, stripped from extension and path information
    """

    filename = os.path.split(full_path_to_file)[-1]
    return os.path.splitext(filename)[0]
