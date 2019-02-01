from django.core.management import BaseCommand, call_command


class Command(BaseCommand):

    def handle(self, *args, **options):
        call_command('runserver', str(options['port']))

    def add_arguments(self, parser):
        parser.add_argument('--port', dest='port', type=int, action='store', default=8000)
