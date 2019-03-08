from decimal import Decimal

from django.test import TestCase
from django.utils import timezone
from unittest.mock import patch

from common.test_mixins import TransactionRequiringMixin
from ledger.balance import Balance
from ledger.exporters import write_balance_to_xlsx, write_profit_loss_to_xlsx
from ledger.profit_loss import ProfitLoss


class ProfitLossExporterTestCase(TransactionRequiringMixin, TestCase):
    def test_that_profit_loss_is_exported_correctly_to_xlsx(self):
        profit_loss = ProfitLoss(self.year)
        expected_contents = [['Account', 'Description', 'Debit', 'Credit'],
                             [self.sales.code, self.sales.name, Decimal('400.00'), None],
                             [self.administration.code, self.administration.name, None, Decimal('300.00')]]
        expected_filename = 'path/to/file.xlsx'
        with patch('ledger.exporters.write_xlsx') as mock_xlsx_writer:
            write_profit_loss_to_xlsx(profit_loss, 'path/to/file')
            mock_xlsx_writer.assert_called_once_with(expected_contents, expected_filename)


class BalanceExporterTestCase(TransactionRequiringMixin, TestCase):
    def test_that_profit_loss_is_exported_correctly_to_xlsx(self):
        end_of_year = timezone.datetime(year=self.year, month=12, day=31).date()
        balance = Balance(end_of_year)
        expected_contents = [['Account', 'Description', 'Debit', 'Account', 'Description', 'Credit'],
                             [1010, 'Bank', Decimal('1200.00'), 2010, 'Creditor: Owner', Decimal('1000.00')],
                             [None, None, None, 2011, 'Creditor: Accountant', Decimal('100.00')],
                             [None, None, None, 3000, 'Equity', Decimal('100.00')]]
        expected_filename = 'path/to/file.xlsx'
        with patch('ledger.exporters.write_xlsx') as mock_xlsx_writer:
            write_balance_to_xlsx(balance, 'path/to/file')
            mock_xlsx_writer.assert_called_once_with(expected_contents, expected_filename)
