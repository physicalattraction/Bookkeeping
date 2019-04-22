import os.path

from django.conf import settings
from django.core.management import BaseCommand

from ledger.exporters import LedgerExporter
from ledger.models import Ledger


class Command(BaseCommand):
    def handle(self, *args, **options):
        year = options['year']
        exporter = LedgerExporter(Ledger.objects.get(year=year))
        finance_filename = os.path.join(settings.BASE_DIR, 'tmp', 'finance_{}'.format(year))
        exporter.write_full_financials_to_xlsx(finance_filename)

    def add_arguments(self, parser):
        parser.add_argument('year', type=int, action='store')
