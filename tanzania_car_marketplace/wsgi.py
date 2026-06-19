import os
from django.core.wsgi import get_wsgi_application
from django.core.management import call_command

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tanzania_car_marketplace.settings')

# Import data on startup (only if data.json exists)
try:
    call_command('loaddata', 'data.json')
    print("✅ Data imported successfully!")
except Exception as e:
    print(f"⚠️ Data import skipped: {e}")

application = get_wsgi_application()