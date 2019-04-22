from django.core.management import BaseCommand

from ledger.importers import LedgerImporter


class Command(BaseCommand):
    def handle(self, *args, **options):
        importer = LedgerImporter()
        importer.import_transactions_from_xlsx(options['file'])

    def add_arguments(self, parser):
        parser.add_argument('file', type=str, action='store', help='Path to the file to import')
