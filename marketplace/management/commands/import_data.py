from django.core.management.base import BaseCommand
from django.core import serializers
import os

class Command(BaseCommand):
    help = 'Import data from data.json'

    def handle(self, *args, **options):
        if not os.path.exists('data.json'):
            self.stdout.write('❌ data.json not found')
            return

        try:
            with open('data.json', 'r') as f:
                data = f.read()

            count = 0
            for obj in serializers.deserialize('json', data):
                obj.save()
                count += 1

            self.stdout.write(self.style.SUCCESS(f'✅ Imported {count} objects'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error: {e}'))