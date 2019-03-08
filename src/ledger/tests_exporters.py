from decimal import Decimal

from django.test import TestCase
from unittest.mock import patch

from common.test_mixins import TransactionRequiringMixin
from ledger.exporters import write_profit_loss_to_xlsx
from ledger.profit_loss import ProfitLoss


class ProfitLossExporterTestCase(TransactionRequiringMixin, TestCase):
    def test_that_profit_loss_is_exported_correctly_to_xlsx(self):
        pl = ProfitLoss(self.year)
        expected_contents = [['Account', 'Description', 'Debit', 'Credit'],
                             [self.sales.code, self.sales.name, Decimal('400.00'), None],
                             [self.administration.code, self.administration.name, None, Decimal('300.00')]]
        expected_filename = 'path/to/file.xlsx'
        with patch('ledger.exporters.write_xlsx') as mock_xlsx_writer:
            write_profit_loss_to_xlsx(pl, 'path/to/file')
            mock_xlsx_writer.assert_called_once_with(expected_contents, expected_filename)
