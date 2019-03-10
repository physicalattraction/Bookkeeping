import os

from django.conf import settings
from django.contrib.auth.models import User
from django.core.management import BaseCommand, call_command
from django.utils import timezone

from accounts.models import ChartOfAccounts
from contacts.models import Contact
from ledger.models import Account, Transaction, Ledger


class Command(BaseCommand):
    def handle(self, *args, **options):
        if os.path.exists(settings.DB_FILE):
            print('Removing {}'.format(settings.DB_FILE))
            os.remove(settings.DB_FILE)
        call_command('migrate')

        if not User.objects.filter(is_staff=True).exists():
            User.objects.create_superuser(username='admin', email='admin@example.com', password='admin')

        owner = Contact.objects.create(name='Eigenaar', account='NL46RABO123456789', email='info@physical.nl')
        accountant = Contact.objects.create(name='Accountant', account='NL46RABO987654321', email='info@accountant.nl')

        call_command('add_default_accounts')
        Account.objects.filter(code='4600').update(contact=accountant)  # Accountantskosten
        Account.objects.filter(code='4710').update(contact=owner)  # Rente lening o/g
        creditor_owner = Account.objects.create(code='1610', name='Crediteuren eigenaar', contact=owner)
        creditor_accountant = Account.objects.create(code='1620', name='Crediteuren accountant', contact=owner)

        ledger = Ledger.objects.create(chart=ChartOfAccounts.objects.get(), year=2018)
        bank = Account.objects.get(code='1100')
        bank_costs = Account.objects.get(code='4640')
        accountant_costs = Account.objects.get(code='4600')
        Transaction.objects.create(ledger=ledger, date=timezone.datetime(year=2018, month=1, day=1).date(),
                                   contact=owner, description='Initial investment', debit_account=bank,
                                   credit_account=creditor_owner, amount=1000)
        Transaction.objects.create(ledger=ledger, date=timezone.datetime(year=2018, month=3, day=28).date(),
                                   invoice_number='SI2016', description='Year finances 2016',
                                   debit_account=accountant_costs, credit_account=creditor_accountant,
                                   amount=100)
        Transaction.objects.create(ledger=ledger, date=timezone.datetime(year=2018, month=4, day=28).date(),
                                   invoice_number='SI2016', description='Year finances 2016',
                                   debit_account=creditor_accountant, credit_account=bank, contact=accountant,
                                   amount=100)
