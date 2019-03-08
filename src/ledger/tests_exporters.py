from decimal import Decimal

from django.test import TestCase
from django.utils import timezone
from openpyxl import Workbook
from unittest.mock import call, patch

from common.test_mixins import TransactionRequiringMixin
from common.utils import Matrix
from ledger.balance import Balance
from ledger.exporters import write_balance_to_xlsx, write_profit_loss_and_balance_to_xlsx, write_profit_loss_to_xlsx
from ledger.profit_loss import ProfitLoss


class ExporterTestCase(TransactionRequiringMixin, TestCase):
    @property
    def profit_loss_contents(self) -> Matrix:
        return [['Account', 'Description', 'Debit', 'Credit'],
                [self.sales.code, self.sales.name, Decimal('400.00'), None],
                [self.administration.code, self.administration.name, None, Decimal('300.00')]]

    @property
    def balance_contents(self) -> Matrix:
        return [['Account', 'Description', 'Debit', 'Account', 'Description', 'Credit'],
                [1010, 'Bank', Decimal('1200.00'), 2010, 'Creditor: Owner', Decimal('1000.00')],
                [None, None, None, 2011, 'Creditor: Accountant', Decimal('100.00')],
                [None, None, None, 3000, 'Equity', Decimal('100.00')]]

    def test_that_profit_loss_is_exported_correctly_to_xlsx(self):
        profit_loss = ProfitLoss(self.year)

        expected_filename = 'path/to/file.xlsx'
        with patch('ledger.exporters.write_xlsx') as mock_xlsx_writer:
            write_profit_loss_to_xlsx(profit_loss, 'path/to/file')
            mock_xlsx_writer.assert_called_once_with(self.profit_loss_contents, expected_filename)

    def test_that_balance_is_exported_correctly_to_xlsx(self):
        end_of_year = timezone.datetime(year=self.year, month=12, day=31).date()
        balance = Balance(end_of_year)

        expected_filename = 'path/to/file.xlsx'
        with patch('ledger.exporters.write_xlsx') as mock_xlsx_writer:
            write_balance_to_xlsx(balance, 'path/to/file')
            mock_xlsx_writer.assert_called_once_with(self.balance_contents, expected_filename)

    def test_that_profit_loss_and_balance_are_exported_correctly_to_xlsx(self):
        end_of_year = timezone.datetime(year=self.year, month=12, day=31).date()
        profit_loss = ProfitLoss(self.year)
        balance = Balance(end_of_year)
        expected_filename = 'path/to/file.xlsx'
        workbook = Workbook()
        with patch('ledger.exporters.write_xlsx', return_value=workbook) as mock_xlsx_writer:
            write_profit_loss_and_balance_to_xlsx(profit_loss, balance, 'path/to/file')
            self.assertEqual(2, mock_xlsx_writer.call_count)
            mock_xlsx_writer.assert_has_calls([
                call(self.profit_loss_contents, expected_filename, worksheet_name='PL'),
                call(self.balance_contents, expected_filename, workbook=workbook, worksheet_name='Balance')
            ])
