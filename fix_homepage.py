import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tanzania_car_marketplace.settings')
django.setup()

from marketplace.models import Car

# Update all cars to be approved
cars = Car.objects.all()
for car in cars:
    car.is_approved = True
    car.save()
    print(f"✅ Approved: {car.title}")

print(f"\n✅ Total cars approved: {cars.count()}")
print("✅ Your cars should now appear on the homepage!")