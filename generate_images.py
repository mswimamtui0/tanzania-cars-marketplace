import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tanzania_car_marketplace.settings')
django.setup()

from marketplace.models import CarListing
from django.core.files.base import ContentFile
from PIL import Image, ImageDraw
import io

def create_car_image(car):
    """Create a professional car image"""
    img = Image.new('RGB', (600, 400), color=(30, 30, 46))
    draw = ImageDraw.Draw(img)
    
    # Car body
    draw.rectangle([100, 200, 500, 280], fill=(78, 115, 223), outline=(255,255,255), width=3)
    draw.ellipse([150, 270, 220, 330], fill=(50,50,50), outline=(255,255,255), width=2)
    draw.ellipse([380, 270, 450, 330], fill=(50,50,50), outline=(255,255,255), width=2)
    
    # Windows
    draw.rectangle([120, 210, 200, 260], fill=(100,100,150))
    draw.rectangle([210, 210, 290, 260], fill=(100,100,150))
    draw.rectangle([300, 210, 380, 260], fill=(100,100,150))
    draw.rectangle([390, 210, 470, 260], fill=(100,100,150))
    
    # Text
    draw.text((180, 80), car.make.upper(), fill=(255,255,255))
    draw.text((180, 115), car.model.upper(), fill=(78,115,223))
    draw.text((180, 320), f"TSh {int(car.price):,}", fill=(0,255,136))
    draw.text((180, 355), f"{car.year} | {int(car.mileage):,} km", fill=(170,170,170))
    
    buffer = io.BytesIO()
    img.save(buffer, format='JPEG', quality=95)
    buffer.seek(0)
    return buffer

print("Generating images for all cars...")
cars = CarListing.objects.all()
count = 0

for car in cars:
    # Delete old image if exists
    if car.images:
        car.images.delete(save=False)
    
    # Create and save new image
    img_buffer = create_car_image(car)
    filename = f"car_{car.id}_{car.make}_{car.model}.jpg"
    car.images.save(filename, ContentFile(img_buffer.getvalue()), save=True)
    count += 1
    print(f"✓ {car.make} {car.model}")

print(f"\n✅ Added images to {count} cars!")