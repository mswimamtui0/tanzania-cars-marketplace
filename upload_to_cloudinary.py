import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tanzania_car_marketplace.settings')
django.setup()

from marketplace.models import CarListing
from django.core.files.base import ContentFile
from PIL import Image, ImageDraw
import io
from cloudinary.uploader import upload

print("Uploading images to Cloudinary...")

for car in CarListing.objects.all():
    # Create image
    img = Image.new('RGB', (600, 400), color=(30, 30, 46))
    draw = ImageDraw.Draw(img)
    
    draw.rectangle([100, 200, 500, 280], fill=(78, 115, 223), outline=(255,255,255), width=3)
    draw.ellipse([150, 270, 220, 330], fill=(50,50,50), outline=(255,255,255), width=2)
    draw.ellipse([380, 270, 450, 330], fill=(50,50,50), outline=(255,255,255), width=2)
    
    draw.text((180, 80), car.make.upper(), fill=(255,255,255))
    draw.text((180, 120), car.model.upper(), fill=(78,115,223))
    draw.text((180, 320), f"TSh {int(car.price):,}", fill=(0,255,136))
    draw.text((180, 355), f"{car.year} | {int(car.mileage):,} km", fill=(170,170,170))
    
    buffer = io.BytesIO()
    img.save(buffer, format='JPEG', quality=90)
    buffer.seek(0)
    
    # Upload directly to Cloudinary
    result = upload(buffer, public_id=f'car_{car.id}', format='jpg')
    
    # Update car with Cloudinary URL
    car.images = result['secure_url']
    car.save()
    print(f"✓ Uploaded {car.make} {car.model} to Cloudinary")

print(f"✅ Done! All images uploaded to Cloudinary.")