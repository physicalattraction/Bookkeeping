from django.db import models

from common.behaviors import Timestampable, UUIDable, Equalable
from contacts.models import Contact


class ChartOfAccounts(UUIDable, Timestampable, Equalable, models.Model):
    """
    In Dutch: grootboek
    """

    pass


class Account(UUIDable, Timestampable, Equalable, models.Model):
    """
    In Dutch: grootboekrekening of rubriek.

    General classification:

    1 Asset accounts
    2 Liability accounts
    3 Equity accounts
    4 Revenue accounts
    5 Expense accounts
    """

    PROFIT_LOSS = 'profit_loss'
    BALANCE = 'balance'
    CHOICES_TYPE = (
        (PROFIT_LOSS, 'On profit/loss sheet'),
        (BALANCE, 'On balance sheet'),
    )

    DEBIT = 'debit'
    CREDIT = 'credit'
    CHOICES_TRANSACTION_TYPE = (
        (DEBIT, 'Debit'),
        (CREDIT, 'Credit'),
    )
    DEBIT_TYPE = 'For profit/loss accounts: debit=cost, credit=profit. ' \
                 'For balance accounts: debit=active, credit=passive'

    chart = models.ForeignKey(ChartOfAccounts, on_delete=models.CASCADE, related_name='accounts')
    code = models.IntegerField(unique=True)
    name = models.CharField(max_length=32, unique=True)
    type = models.CharField(max_length=16, choices=CHOICES_TYPE, help_text='Where to put the account')
    debit_type = models.CharField(max_length=16, choices=CHOICES_TRANSACTION_TYPE, help_text=DEBIT_TYPE)
    contact = models.ForeignKey(Contact, null=True, blank=True, default=None, related_name='accounts',
                                on_delete=models.PROTECT, help_text='Linked contact, in use for debitors and creditors')

    class Meta:
        ordering = ['code']

    def clean(self):
        # TODO: Remove once there can be multiple ChartOfAccounts
        if not getattr(self, 'chart', None):
            self.chart = ChartOfAccounts.objects.get()
        super().clean()

    def __str__(self):
        return '{} - {}'.format(self.code, self.name)


class Ledger(UUIDable, Timestampable, Equalable, models.Model):
    chart = models.ForeignKey(ChartOfAccounts, on_delete=models.PROTECT, related_name='ledgers')
    year = models.IntegerField()

    class Meta:
        ordering = ['chart', 'year']

    def clean(self):
        # TODO: Remove once there can be multiple ChartOfAccounts
        if not getattr(self, 'chart', None):
            self.chart = ChartOfAccounts.objects.get()
        super().clean()

    def __str__(self):
        return str(self.year)


class Transaction(UUIDable, Timestampable, Equalable, models.Model):
    date = models.DateField(help_text='Transaction date')
    ledger = models.ForeignKey(Ledger, on_delete=models.CASCADE, related_name='transactions')
    description = models.CharField(max_length=128, help_text='Long description of the transaction')
    invoice_number = models.CharField(max_length=32, blank=True, default='', help_text='Invoice number from invoicee')
    contact = models.ForeignKey(Contact, null=True, blank=True, default=None, related_name='transactions',
                                on_delete=models.PROTECT)
    debit_account = models.ForeignKey(Account, on_delete=models.PROTECT, related_name='debit_transactions')
    credit_account = models.ForeignKey(Account, on_delete=models.PROTECT, related_name='credit_transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    # TODO: Think of a way how to model multiple debit lines and credit lines in one transaction,
    #       e.g. with model TransactionDetail

    class Meta:
        ordering = ['date', 'description']

    def clean(self):
        # TODO: Pass correct chart of accounts once there can be multiple
        self.ledger, _ = Ledger.objects.get_or_create(year=self.date.year, chart=ChartOfAccounts.objects.get())
        super().clean()
