from decimal import Decimal
from unittest.mock import Mock

from django.test import TestCase
from django.utils import timezone

from contacts.models import Contact
from ledger.balance import Balance, BalanceItem
from ledger.models import Account, ChartOfAccounts, Ledger, Transaction


class BalanceItemTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.chart = ChartOfAccounts.objects.create()
        cls.bank = Account.objects.create(chart=cls.chart, code=1000, name='Bank',
                                          type=Account.BALANCE, debit_type=Account.DEBIT)

    def test_balance_item_initialization_with_none(self):
        line = BalanceItem(self.bank, None)
        self.assertIsNone(line.value)

    def test_balance_item_initialization_with_ints(self):
        line = BalanceItem(self.bank, 1)
        self.assertEqual(Decimal('1'), line.value)

    def test_balance_item_initialization_with_floats(self):
        line = BalanceItem(self.bank, 2.144)
        self.assertEqual(Decimal('2.14'), line.value)

    def test_balance_item_initialization_with_decimals(self):
        line = BalanceItem(self.bank, Decimal('2.345'))
        self.assertEqual(Decimal('2.34'), line.value)


# TODO: Consolidate test case setup with ProfitLossTestCase
class BalanceTestCase(TestCase):
    # TODO: Test with different dates

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.owner = Contact.objects.create(name='Owner', account='bank owner', email='info@physical.nl')
        cls.accountant = Contact.objects.create(name='Accountant', account='bank accountant',
                                                email='info@accountant.nl')

        cls.chart = ChartOfAccounts.objects.create()
        cls.administration = Account.objects.create(chart=cls.chart, code=5010, name='Administration',
                                                    type=Account.PROFIT_LOSS, debit_type=Account.DEBIT)
        cls.sales = Account.objects.create(chart=cls.chart, code=4100, name='Sales income',
                                           type=Account.PROFIT_LOSS, debit_type=Account.CREDIT)
        cls.bank = Account.objects.create(chart=cls.chart, code=1010, name='Bank',
                                          type=Account.BALANCE, debit_type=Account.DEBIT)
        cls.creditor_owner = Account.objects.create(chart=cls.chart, code=2010, name='Creditor: Owner',
                                                    contact=cls.accountant,
                                                    type=Account.BALANCE, debit_type=Account.CREDIT)
        cls.creditor_accountant = Account.objects.create(chart=cls.chart, code=2011, name='Creditor: Accountant',
                                                         contact=cls.accountant,
                                                         type=Account.BALANCE, debit_type=Account.CREDIT)

        cls.year = 2018
        cls.ledger = Ledger.objects.create(chart=cls.chart, year=cls.year)
        cls.date = timezone.datetime(year=cls.year, month=1, day=1).date()

    def test_calculate_balance(self):
        Transaction.objects.create(ledger=self.ledger, date=self.date,
                                   description='Initial investment', debit_account=self.bank,
                                   credit_account=self.creditor_owner, amount=1000)
        Transaction.objects.create(ledger=self.ledger, date=self.date, description='Accountant sent invoice',
                                   debit_account=self.administration, credit_account=self.creditor_accountant,
                                   amount=300)
        Transaction.objects.create(ledger=self.ledger, date=self.date, description='Sales',
                                   debit_account=self.bank, credit_account=self.sales, amount=400)
        Transaction.objects.create(ledger=self.ledger, date=self.date, description='Partial payment accountant',
                                   debit_account=self.creditor_accountant, credit_account=self.bank, amount=200)

        balance = Balance(self.date)
        balance._calculate_balance()

        # Ensure that equity account is created
        equity = Account.objects.get(name='Equity')

        # Verify the calculated balance items
        expected_debit_items = [BalanceItem(self.bank, 1200)]
        expected_credit_items = [BalanceItem(self.creditor_owner, 1000),
                                 BalanceItem(self.creditor_accountant, 100),
                                 BalanceItem(equity, 100)]
        self.assertListEqual(expected_debit_items, balance.debit_balance_items)
        self.assertListEqual(expected_credit_items, balance.credit_balance_items)

    def test_get_account_result_positive_debit_account(self):
        Transaction.objects.create(uuid='1', ledger=self.ledger, date=self.date, description='Payment received',
                                   debit_account=self.bank, credit_account=self.creditor_owner, amount=300)
        Transaction.objects.create(uuid='2', ledger=self.ledger, date=self.date, description='Payment made',
                                   debit_account=self.creditor_owner, credit_account=self.bank, amount=200)
        result = Balance._get_account_result(Mock(Balance), self.bank,
                                             Transaction.objects.filter(uuid='1'), Transaction.objects.filter(uuid='2'))
        self.assertEqual(Decimal(100), result)

    def test_get_account_result_negative_debit_account(self):
        Transaction.objects.create(uuid='1', ledger=self.ledger, date=self.date, description='Payment received',
                                   debit_account=self.bank, credit_account=self.creditor_owner, amount=200)
        Transaction.objects.create(uuid='2', ledger=self.ledger, date=self.date, description='Payment made',
                                   debit_account=self.creditor_owner, credit_account=self.bank, amount=300)
        result = Balance._get_account_result(Mock(Balance), self.bank,
                                             Transaction.objects.filter(uuid='1'), Transaction.objects.filter(uuid='2'))
        self.assertEqual(Decimal(-100), result)

    def test_get_account_result_positive_credit_account(self):
        Transaction.objects.create(uuid='1', ledger=self.ledger, date=self.date, description='Accountant sent invoice',
                                   debit_account=self.administration, credit_account=self.creditor_accountant,
                                   amount=300)
        Transaction.objects.create(uuid='2', ledger=self.ledger, date=self.date, description='Invoice partly paid',
                                   debit_account=self.creditor_accountant, credit_account=self.bank, amount=200)
        result = Balance._get_account_result(Mock(Balance), self.creditor_accountant,
                                             Transaction.objects.filter(uuid='2'), Transaction.objects.filter(uuid='1'))
        self.assertEqual(Decimal(100), result)

    def test_get_account_result_negative_credit_account(self):
        Transaction.objects.create(uuid='1', ledger=self.ledger, date=self.date, description='Accountant sent invoice',
                                   debit_account=self.administration, credit_account=self.creditor_accountant,
                                   amount=200)
        Transaction.objects.create(uuid='2', ledger=self.ledger, date=self.date, description='Previous invoice paid',
                                   debit_account=self.creditor_accountant, credit_account=self.bank, amount=300)
        result = Balance._get_account_result(Mock(Balance), self.creditor_accountant,
                                             Transaction.objects.filter(uuid='2'), Transaction.objects.filter(uuid='1'))
        self.assertEqual(Decimal(-100), result)

    def test_debit_and_credit_sum(self):
        balance = Balance(self.date)
        self.assertEqual(Decimal(0), balance.debit_sum)
        self.assertEqual(Decimal(0), balance.credit_sum)

        balance.debit_balance_items = [BalanceItem(account=self.bank, value=Decimal(500))]
        balance.credit_balance_items = [BalanceItem(account=self.creditor_owner, value=Decimal(500)),
                                        BalanceItem(account=self.creditor_accountant, value=Decimal(200))]
        self.assertEqual(Decimal(500), balance.debit_sum)
        self.assertEqual(Decimal(700), balance.credit_sum)

    def test_lines(self):
        balance = Balance(self.date)
        balance.debit_balance_items = [BalanceItem(account=self.bank, value=Decimal(500))]
        balance.credit_balance_items = [BalanceItem(account=self.creditor_owner, value=Decimal(500)),
                                        BalanceItem(account=self.creditor_accountant, value=Decimal(200))]
        expected_lines = [['Bank', '500.00', 'Creditor: Owner', '500.00'], ['', '', 'Creditor: Accountant', '200.00']]
        self.assertEqual(expected_lines, balance.lines)
