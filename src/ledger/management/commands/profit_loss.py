from django.core.management import BaseCommand
from django.utils import timezone

from ledger.balance import Balance, ProfitLoss


class Command(BaseCommand):
    def handle(self, *args, **options):
        year = options['year']
        ProfitLoss(year, '../tmp/{}_profit_loss.csv'.format(year))

        begin_of_year = timezone.datetime(year=year - 1, month=12, day=31).date()
        end_of_year = timezone.datetime(year=year, month=12, day=31).date()
        print(type(begin_of_year))
        Balance(begin_of_year, '../tmp/{}_balance_begin.csv'.format(year))
        Balance(end_of_year, '../tmp/{}_balance_end.csv'.format(year))

    def add_arguments(self, parser):
        parser.add_argument('year', type=int, action='store')
