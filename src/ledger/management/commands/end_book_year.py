import os.path

from django.conf import settings
from django.core.management import BaseCommand
from django.utils import timezone

from ledger.balance import Balance
from ledger.exporters import write_profit_loss_and_balance_to_xlsx
from ledger.profit_loss import ProfitLoss


class Command(BaseCommand):
    def handle(self, *args, **options):
        year = options['year']
        profit_loss = ProfitLoss(year)

        end_of_year = timezone.datetime(year=year, month=12, day=31).date()
        balance = Balance(end_of_year)

        finance_filename = os.path.join(settings.BASE_DIR, 'tmp', 'finance_{}'.format(year))
        write_profit_loss_and_balance_to_xlsx(profit_loss, balance, finance_filename)

    def add_arguments(self, parser):
        parser.add_argument('year', type=int, action='store')
