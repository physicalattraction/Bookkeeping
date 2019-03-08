from datetime import date
from decimal import Decimal

import datetime
from django.db.models import QuerySet, Sum
from typing import List

from common.utils import write_csv, Numeric
from ledger.models import Account, ChartOfAccounts, Transaction


class BalanceItem:
    def __init__(self, account: Account = None, value: Numeric = None):
        self.account = account
        self.value = Decimal(value).quantize(Decimal('.01')) if value is not None else None

    @property
    def account_str(self) -> str:
        """
        Return a string representation of the account, or empty string if there is no account
        """

        return self.account.name if self.account is not None else ''

    @property
    def value_str(self) -> str:
        """
        Return a string representation of the value, or empty string if there is no value
        """

        return str(self.value) if self.value is not None else ''

    def __eq__(self, other):
        return self.account == other.account and self.value == other.value


class Balance:
    debit_balance_items: List[BalanceItem]
    credit_balance_items: List[BalanceItem]

    def __init__(self, date: datetime.date):
        """
        Generate a balance on the given date by collecting all transactions prior to this date
        """

        # TODO: Also enable a starting_date, so one can calculate a difference balance
        # TODO: Input for who to make the balance, instead of assuming there is only one user owning transactions

        self.date = date
        self.accounts = Account.objects.filter(type=Account.BALANCE)
        self._calculate_balance()

    # TODO: Write system tests for this function
    def _calculate_balance(self):
        """
        Calculate and store in the object all balance items
        """

        debit_transactions = Transaction.objects.filter(debit_account__in=self.accounts, date__lte=self.date)
        credit_transactions = Transaction.objects.filter(credit_account__in=self.accounts, date__lte=self.date)
        self.debit_balance_items = []
        self.credit_balance_items = []
        accounts = self.accounts.order_by('code')
        for account in accounts:
            account_result = self._get_account_result(account, debit_transactions, credit_transactions)
            if account_result == 0:
                continue
            if account.debit_type == Account.DEBIT:
                self.debit_balance_items.append(BalanceItem(account, account_result))
            else:
                self.credit_balance_items.append(BalanceItem(account, account_result))

        # Add equity item, which is the result of all other transactions
        equity, _ = Account.objects.get_or_create(chart=ChartOfAccounts.objects.get(), name='Equity',
                                                  defaults={'code': 3000, 'type': Account.BALANCE,
                                                            'debit_type': Account.CREDIT})
        self.credit_balance_items.append(BalanceItem(equity, self.debit_sum - self.credit_sum))

    def _get_account_result(self, account: Account, debit_transactions: QuerySet,
                            credit_transactions: QuerySet) -> Decimal:
        """
        Get the balance account result from the given transactions

        For accounts of debit_type 'debit', the result is positive if the debit transactions are greater than the
        credit transactions for this account. For accounts of debit_type 'credit', the result is positive if the
        credit transactions are greater than the debit transactions.
        """

        account_debits = debit_transactions.filter(debit_account=account)
        account_debits_sum = account_debits.aggregate(Sum('amount'))['amount__sum'] or 0
        account_credits = credit_transactions.filter(credit_account=account)
        account_credits_sum = account_credits.aggregate(Sum('amount'))['amount__sum'] or 0
        if account.debit_type == Account.DEBIT:
            return account_debits_sum - account_credits_sum
        else:
            return account_credits_sum - account_debits_sum

    @property
    def debit_sum(self) -> Decimal:
        """
        Return the sum of all debit balance items
        """

        return sum([item.value for item in self.debit_balance_items])

    @property
    def credit_sum(self) -> Decimal:
        """
        Return the sum of all credit balance items
        """

        return sum([item.value for item in self.credit_balance_items])

    @property
    def total_line(self) -> [str, str, str, str]:
        return ['Total', str(self.debit_sum), 'Total', str(self.credit_sum)]

    @property
    def lines(self) -> [[str, str, str, str]]:
        """
        Return a list of lines on the balance sheet

        If there are more debit or credit items on the balance, the difference is on the other side is filled with
        empty items

        :return: List of line [debit account, value, credit account, value]
        """

        # TODO: Move this code to Balance exporter

        debit_balance_items = self.debit_balance_items
        credit_balance_items = self.credit_balance_items

        # Add empty items
        lines_longer = len(debit_balance_items) - len(credit_balance_items)
        if lines_longer > 0:
            credit_balance_items += [BalanceItem()] * lines_longer
        elif lines_longer < 0:
            debit_balance_items += [BalanceItem()] * -lines_longer

        return [[items[0].account_str, items[0].value_str, items[1].account_str, items[1].value_str]
                for items in zip(debit_balance_items, credit_balance_items)]

    def __repr__(self):
        return LINETERMINATOR.join([self.HEADER] + [repr(pll) for pll in self.lines] + [self.total_line])

    def save(self, output_file: str):
        write_csv(self.HEADER, self.lines + [self.total_line], output_file)
