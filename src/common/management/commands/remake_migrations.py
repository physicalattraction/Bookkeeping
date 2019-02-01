import glob
import os

from django.conf import settings
from django.core.management import BaseCommand, call_command


class Command(BaseCommand):
    def handle(self, *args, **options):

        for app in settings.PROJECT_APPS:
            migrations_dir = os.path.join(settings.BASE_DIR, 'src', app, 'migrations')
            if os.path.exists(migrations_dir):
                for file in glob.glob(os.path.join(migrations_dir, '00*.py')):
                    print('Removing {}'.format(file))
                    os.remove(file)
        call_command('makemigrations')
