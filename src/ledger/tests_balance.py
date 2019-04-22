from decimal import Decimal
from unittest import skip

from django.test import TestCase
from unittest.mock import Mock

from common.test_mixins import AccountRequiringMixin, LedgerRequiringMixin
from ledger.balance import Balance, BalanceItem
from ledger.models import Account, Transaction


class BalanceItemTestCase(AccountRequiringMixin,  TestCase):
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


class BalanceTestCase(LedgerRequiringMixin, TestCase):
    # TODO: Test with different dates
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
        equity = Account.objects.get(name=Balance.equity_name)

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
