# add_images_simple.py
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tanzania_car_marketplace.settings')
django.setup()

from marketplace.models import CarListing
from django.core.files.base import ContentFile
from PIL import Image, ImageDraw
import io

print("Adding images to cars...")

cars = CarListing.objects.all()
count = 0

for car in cars:
    # Create a simple colored rectangle
    img = Image.new('RGB', (400, 200), color='#667eea')
    draw = ImageDraw.Draw(img)
    
    # Add text
    text = f"{car.make} {car.model}\n{car.year}\nTSh {car.price:,.0f}"
    draw.text((50, 80), text, fill='white')
    
    # Save to bytes
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG')
    img_byte_arr.seek(0)
    
    # Save to car
    filename = f"{car.make}_{car.model}_{car.id}.jpg"
    car.images.save(filename, ContentFile(img_byte_arr.getvalue()), save=True)
    count += 1
    print(f"✓ Added image for {car.make} {car.model}")

print(f"\n✅ Added images to {count} cars!")