import os

from django.conf import settings
from django.contrib.auth.models import User
from django.core.management import BaseCommand, call_command
from django.utils import timezone

from contacts.models import Contact
from ledger.models import Account, ChartOfAccounts, Transaction


class Command(BaseCommand):
    def handle(self, *args, **options):
        if os.path.exists(settings.DB_FILE):
            print('Removing {}'.format(settings.DB_FILE))
            os.remove(settings.DB_FILE)
        call_command('migrate')

        if not User.objects.filter(is_staff=True).exists():
            User.objects.create_superuser(username='admin', email='admin@example.com', password='admin')

        owner = Contact.objects.create(name='Owner', account='NL46RABO123456789', email='info@physical.nl')
        accountant = Contact.objects.create(name='Accountant', account='NL46RABO987654321', email='info@accountant.nl')

        chart = ChartOfAccounts.objects.create()
        administration = Account.objects.create(chart=chart, code=5010, name='Administration', type=Account.PROFIT_LOSS,
                                               debit_type=Account.DEBIT)
        bank = Account.objects.create(chart=chart, code=1010, name='Bank', type=Account.BALANCE,
                                      debit_type=Account.DEBIT)
        creditor_owner = Account.objects.create(chart=chart, code=2010, name='Creditor: Owner', contact=accountant,
                                                type=Account.BALANCE, debit_type=Account.CREDIT)
        creditor_accountant = Account.objects.create(chart=chart, code=2011, name='Creditor: Accountant', contact=accountant,
                                                     type=Account.BALANCE, debit_type=Account.CREDIT)

        Transaction.objects.create(date=timezone.datetime(year=2018, month=1, day=1).date(), contact=owner,
                                   description='Initial investment', debit_account=bank, credit_account=creditor_owner,
                                   amount=1000)
        Transaction.objects.create(date=timezone.datetime(year=2018, month=3, day=28).date(), invoice_number='SI2016',
                                   description='Year finances 2016', debit_account=administration,
                                   credit_account=creditor_accountant, contact=accountant, amount=100)
        Transaction.objects.create(date=timezone.datetime(year=2018, month=4, day=28).date(), invoice_number='SI2016',
                                   description='Year finances 2016', debit_account=creditor_accountant,
                                   credit_account=bank, contact=accountant, amount=100)
