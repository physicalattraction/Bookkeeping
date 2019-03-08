from django.test import TestCase
from django.utils import timezone

from contacts.models import Contact
from ledger.models import Account, ChartOfAccounts, Ledger


class ContactRequiringMixin(TestCase):
    owner: Contact
    accountant: Contact

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.owner = Contact.objects.create(name='Owner', account='bank owner', email='info@physical.nl')
        cls.accountant = Contact.objects.create(name='Accountant', account='bank accountant',
                                                email='info@accountant.nl')


class AccountRequiringMixin(ContactRequiringMixin):
    chart: ChartOfAccounts
    administration: Account
    sales: Account
    bank: Account
    creditor_owner: Account
    creditor_accountant: Account

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

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


class TransactionRequiringMixin(AccountRequiringMixin):
    year: int
    ledger: Ledger
    date: timezone.datetime

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.year = 2018
        cls.ledger = Ledger.objects.create(chart=cls.chart, year=cls.year)
        cls.date = timezone.datetime(year=cls.year, month=1, day=1).date()
