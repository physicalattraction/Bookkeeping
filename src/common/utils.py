import csv
from decimal import Decimal

from typing import Union

Numeric = Union[Decimal, float, int]
SEPARATOR = ','
LINETERMINATOR = '\n'


def write_csv(header: [str], lines: [str], full_path_to_file: str):
    with open(full_path_to_file, 'w') as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow(header)
        for line in lines:
            if line is not None:
                csv_writer.writerow(line)
