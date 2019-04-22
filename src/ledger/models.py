from decimal import Decimal

from django.db import models

from accounts.models import Account, ChartOfAccounts
from common.behaviors import Equalable, Timestampable, UUIDable
from contacts.models import Contact


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
    # Get rid of UUIDable and use ids instead
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
        if not getattr(self, 'ledger', None):
            # TODO: Pass correct chart of accounts once there can be multiple
            self.ledger, _ = Ledger.objects.get_or_create(year=self.date.year, chart=ChartOfAccounts.objects.get())
        if self.description:
            self.invoice_number = str(self.description)
        if self.invoice_number:
            self.invoice_number = str(self.invoice_number)
        if not getattr(self, 'contact', None):
            self.contact = self.debit_account.contact or self.credit_account.contact
        if isinstance(self.amount, str):
            self.amount = Decimal(self.amount.replace('€', '').replace('$', ''))
