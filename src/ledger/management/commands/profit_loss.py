from django.conf import settings
from django.core.management import BaseCommand
from django.utils import timezone
import os.path
from ledger.exporters import write_profit_loss_to_xlsx
from ledger.profit_loss import ProfitLoss


class Command(BaseCommand):
    def handle(self, *args, **options):
        year = options['year']
        profit_loss = ProfitLoss(year)
        profit_loss_filename = os.path.join(settings.BASE_DIR, 'tmp', 'profit_loss_{}'.format(year))
        write_profit_loss_to_xlsx(profit_loss, profit_loss_filename)

        # begin_of_year = timezone.datetime(year=year - 1, month=12, day=31).date()
        # end_of_year = timezone.datetime(year=year, month=12, day=31).date()
        # print(type(begin_of_year))
        # Balance(begin_of_year, '../tmp/{}_balance_begin.csv'.format(year))
        # Balance(end_of_year, '../tmp/{}_balance_end.csv'.format(year))

    def add_arguments(self, parser):
        parser.add_argument('year', type=int, action='store')
