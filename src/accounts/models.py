from django.db import models
from django.db.models import Manager

from common.behaviors import Equalable, Timestampable, UUIDable
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
    4 Expense accounts indirectly related to revenue
    5 Expense accounts directly related to revenue
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

    # TODO: Build in hierarchy in accounts
    chart = models.ForeignKey(ChartOfAccounts, on_delete=models.CASCADE, related_name='accounts')
    code = models.CharField(max_length=4, unique=True)  # Code can start with 0, and hence is not an integer
    name = models.CharField(max_length=32)  # Name is not unique, e.g. company tax can be both on PL and on Balance
    type = models.CharField(max_length=16, choices=CHOICES_TYPE, help_text='Where to put the account')
    debit_type = models.CharField(max_length=16, choices=CHOICES_TRANSACTION_TYPE, help_text=DEBIT_TYPE)
    contact = models.ForeignKey(Contact, null=True, blank=True, default=None, related_name='accounts',
                                on_delete=models.PROTECT, help_text='Linked contact, in use for debitors and creditors')

    class Meta:
        ordering = ['code']

    def clean(self):
        # TODO: Remove once there can be multiple ChartOfAccounts
        if not getattr(self, 'chart', None):
            self.chart, _ = ChartOfAccounts.objects.get_or_create()
        super().clean()

    def __str__(self):
        return '{} - {}'.format(self.code, self.name)
