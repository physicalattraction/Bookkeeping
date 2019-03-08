from decimal import Decimal

from django.test import TestCase
from django.utils import timezone

from common.test_mixins import TransactionRequiringMixin
from ledger.models import Account, ChartOfAccounts, Transaction
from ledger.profit_loss import ProfitLoss, ProfitLossLine


class ProfitLossLineTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.chart = ChartOfAccounts.objects.create()
        cls.sales = Account.objects.create(chart=cls.chart, code=4100, name='Sales income',
                                           type=Account.PROFIT_LOSS, debit_type=Account.CREDIT)

    def test_profit_line_initialization_with_none(self):
        line = ProfitLossLine(self.sales, None, None)
        self.assertIsNone(line.debit)
        self.assertIsNone(line.credit)

    def test_profit_line_initialization_with_ints(self):
        line = ProfitLossLine(self.sales, 0, 1)
        self.assertEqual(Decimal('0'), line.debit)
        self.assertEqual(Decimal('1'), line.credit)

    def test_profit_line_initialization_with_floats(self):
        line = ProfitLossLine(self.sales, 0.0, 2.144)
        self.assertEqual(Decimal('0.0'), line.debit)
        self.assertEqual(Decimal('2.14'), line.credit)

    def test_profit_line_initialization_with_decimals(self):
        line = ProfitLossLine(self.sales, Decimal(0), Decimal('2.345'))
        self.assertEqual(Decimal('0.0'), line.debit)
        self.assertEqual(Decimal('2.34'), line.credit)


class ProfitLossTestCase(TransactionRequiringMixin, TestCase):

    def test_that_profit_loss_calculates_loss_correctly(self):
        Transaction.objects.create(ledger=self.ledger, date=timezone.datetime(year=self.year, month=3, day=28).date(),
                                   description='Accountant invoice', debit_account=self.administration,
                                   credit_account=self.creditor_accountant, amount=100)
        pl = ProfitLoss(year=2018)
        self.assertEqual(1, len(pl.profit_loss_lines))
        self.assertEqual(pl.total.account.name, 'Loss')
        self.assertIsNone(pl.total.debit)
        self.assertEqual(pl.total.credit, Decimal(100))

        Transaction.objects.create(ledger=self.ledger, date=timezone.datetime(year=self.year, month=3, day=28).date(),
                                   description='New client', debit_account=self.bank,
                                   credit_account=self.sales, amount=50)
        pl = ProfitLoss(year=2018)
        self.assertEqual(2, len(pl.profit_loss_lines))
        self.assertEqual(pl.total.account.name, 'Loss')
        self.assertIsNone(pl.total.debit)
        self.assertEqual(pl.total.credit, Decimal(50))

    def test_that_profit_loss_calculates_profit_correctly(self):
        Transaction.objects.create(ledger=self.ledger, date=timezone.datetime(year=self.year, month=3, day=28).date(),
                                   description='New client', debit_account=self.bank,
                                   credit_account=self.sales, amount=100)
        pl = ProfitLoss(year=2018)
        self.assertEqual(1, len(pl.profit_loss_lines))
        self.assertEqual(pl.total.account.name, 'Profit')
        self.assertEqual(pl.total.debit, Decimal(100))
        self.assertIsNone(pl.total.credit)

        Transaction.objects.create(ledger=self.ledger, date=timezone.datetime(year=self.year, month=3, day=28).date(),
                                   description='Accountant invoice', debit_account=self.administration,
                                   credit_account=self.creditor_accountant, amount=50)
        pl = ProfitLoss(year=2018)
        self.assertEqual(2, len(pl.profit_loss_lines))
        self.assertEqual(pl.total.account.name, 'Profit')
        self.assertEqual(pl.total.debit, Decimal(50))
        self.assertIsNone(pl.total.credit)

    def test_that_profit_loss_removes_lines_that_cancel(self):
        Transaction.objects.create(ledger=self.ledger, date=timezone.datetime(year=self.year, month=3, day=28).date(),
                                   description='New client', debit_account=self.bank,
                                   credit_account=self.sales, amount=100)
        Transaction.objects.create(ledger=self.ledger, date=timezone.datetime(year=self.year, month=3, day=28).date(),
                                   description='Credit invoice', debit_account=self.sales,
                                   credit_account=self.bank, amount=100)
        pl = ProfitLoss(year=2018)
        self.assertEqual(0, len(pl.profit_loss_lines))
