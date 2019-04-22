from decimal import Decimal

import datetime
from django.test import TestCase
from django.utils import timezone
from openpyxl import Workbook
from unittest.mock import call, patch

from common.test_mixins import TransactionRequiringMixin
from common.utils import Matrix
from ledger.balance import Balance
from ledger.exporters import LedgerExporter
from ledger.profit_loss import ProfitLoss


class ExporterTestCase(TransactionRequiringMixin, TestCase):
    filename = 'path/to/file.xlsx'

    def setUp(self):
        self.exporter = LedgerExporter(year=2018)

    @property
    def ledger_contents(self) -> Matrix:
        return [
            ['ID', 'Date', 'Description', 'Invoice number', 'Contact', 'Account code', 'Account name', 'Debit',
             'Credit'],

            [1, datetime.date(2018, 1, 1), 'Initial investment', '', None, '1010', 'Bank', Decimal('1000.00'), None],
            [None, None, None, None, 'Owner', '2010', 'Creditor: Owner', None, Decimal('1000.00')],

            [2, datetime.date(2018, 1, 2), 'Accountant sent invoice', 'INV-123', None, '5010', 'Administration',
             Decimal('300.00'), None],
            [None, None, None, None, 'Accountant', '2011', 'Creditor: Accountant', None, Decimal('300.00')],

            [3, datetime.date(2018, 1, 3), 'Sales', '', None, '1010', 'Bank', Decimal('400.00'), None],
            [None, None, None, None, None, '4100', 'Sales income', None, Decimal('400.00')],

            [4, datetime.date(2018, 1, 4), 'Partial payment accountant', '', 'Accountant', '2011',
             'Creditor: Accountant', Decimal('200.00'), None],
            [None, None, None, None, None, '1010', 'Bank', None, Decimal('200.00')]
        ]

    @property
    def profit_loss_contents(self) -> Matrix:
        return [['Account', 'Description', 'Debit', 'Credit'],
                [self.sales.code, self.sales.name, Decimal('400.00'), None],
                [self.administration.code, self.administration.name, None, Decimal('300.00')],
                [None, 'Winst', None, Decimal('100.00')],
                [None, 'Total', Decimal('400.00'), Decimal('400.00')]]

    @property
    def balance_contents(self) -> Matrix:
        return [['Account', 'Description', 'Debit', 'Account', 'Description', 'Credit'],
                ['1010', 'Bank', Decimal('1200.00'), '2010', 'Creditor: Owner', Decimal('1000.00')],
                [None, None, None, '2011', 'Creditor: Accountant', Decimal('100.00')],
                [None, None, None, '1900', 'Eigen vermogen', Decimal('100.00')],
                [None, 'Total', Decimal('1200.00'), None, 'Total', Decimal('1200.00')]]

    def test_that_ledger_is_exported_correctly(self):
        with patch('ledger.exporters.write_xlsx') as mock_xlsx_writer:
            self.exporter.write_ledger_to_xlsx(self.filename)
            mock_xlsx_writer.assert_called_once_with(self.ledger_contents, self.filename)

    def test_that_profit_loss_is_exported_correctly_to_xlsx(self):
        with patch('ledger.exporters.write_xlsx') as mock_xlsx_writer:
            self.exporter.write_profit_loss_to_xlsx(self.filename)
            mock_xlsx_writer.assert_called_once_with(self.profit_loss_contents, self.filename)

    def test_that_balance_is_exported_correctly_to_xlsx(self):
        with patch('ledger.exporters.write_xlsx') as mock_xlsx_writer:
            self.exporter.write_balance_to_xlsx(self.filename)
            mock_xlsx_writer.assert_called_once_with(self.balance_contents, self.filename)

    def test_that_profit_loss_and_balance_are_exported_correctly_to_xlsx(self):
        workbook = Workbook()
        with patch('ledger.exporters.write_xlsx', return_value=workbook) as mock_xlsx_writer:
            self.exporter.write_full_financials_to_xlsx('path/to/file')
            self.assertEqual(2, mock_xlsx_writer.call_count)
            mock_xlsx_writer.assert_has_calls([
                call(self.profit_loss_contents, self.filename, worksheet_name='PL'),
                call(self.balance_contents, self.filename, workbook=workbook, worksheet_name='Balance')
            ])
