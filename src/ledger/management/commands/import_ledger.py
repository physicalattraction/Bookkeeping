from django.core.management import BaseCommand

from ledger.importers import import_transactions_from_xlsx


class Command(BaseCommand):
    def handle(self, *args, **options):
        import_transactions_from_xlsx(options['file'])

    def add_arguments(self, parser):
        parser.add_argument('file', type=str, action='store', help='Path to the file to import')
