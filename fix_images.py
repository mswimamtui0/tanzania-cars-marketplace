import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tanzania_car_marketplace.settings')
django.setup()

from marketplace.models import CarListing
from django.core.files.base import ContentFile
from PIL import Image, ImageDraw
import io

print("Generating images for all cars...")

cars = CarListing.objects.all()
count = 0

for car in cars:
    # Create image
    img = Image.new('RGB', (600, 400), color=(30, 30, 46))
    draw = ImageDraw.Draw(img)
    
    # Draw car
    draw.rectangle([100, 200, 500, 280], fill=(78, 115, 223), outline=(255,255,255), width=3)
    draw.ellipse([150, 270, 220, 330], fill=(50,50,50), outline=(255,255,255), width=2)
    draw.ellipse([380, 270, 450, 330], fill=(50,50,50), outline=(255,255,255), width=2)
    
    # Add text
    draw.text((180, 80), car.make.upper(), fill=(255,255,255))
    draw.text((180, 115), car.model.upper(), fill=(78,115,223))
    draw.text((180, 320), f"TSh {int(car.price):,}", fill=(0,255,136))
    draw.text((180, 355), f"{car.year} | {int(car.mileage):,} km", fill=(170,170,170))
    
    # Save
    buffer = io.BytesIO()
    img.save(buffer, format='JPEG', quality=95)
    buffer.seek(0)
    
    # Delete old image if exists
    if car.images:
        car.images.delete(save=False)
    
    # Save new image
    car.images.save(f'car_{car.id}.jpg', ContentFile(buffer.getvalue()), save=True)
    count += 1
    print(f"✓ Image added for {car.make} {car.model}")

print(f"\n✅ Added images to {count} cars!")