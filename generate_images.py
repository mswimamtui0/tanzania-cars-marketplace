import os
import django
from django.conf import settings
from django.core.files import File
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import random

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tanzania_car_marketplace.settings')
django.setup()

from marketplace.models import Car


def generate_car_image(car):
    """Generate a simple placeholder image for a car."""
    # Create a new image
    img = Image.new('RGB', (800, 600), color=(random.randint(50, 200), random.randint(50, 200), random.randint(50, 200)))
    draw = ImageDraw.Draw(img)
    
    # Add car text
    text = f"{car.brand} {car.model}"
    try:
        font = ImageFont.truetype("arial.ttf", 60)
    except:
        font = ImageFont.load_default()
    
    # Get text size
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Center the text
    x = (800 - text_width) // 2
    y = (600 - text_height) // 2
    
    # Draw white background for text
    draw.rectangle([x-20, y-20, x+text_width+20, y+text_height+20], fill='white')
    draw.text((x, y), text, fill='black', font=font)
    
    # Add price
    price_text = f"TSh {car.price:,.0f}"
    try:
        font_small = ImageFont.truetype("arial.ttf", 40)
    except:
        font_small = ImageFont.load_default()
    
    price_bbox = draw.textbbox((0, 0), price_text, font=font_small)
    price_width = price_bbox[2] - price_bbox[0]
    price_x = (800 - price_width) // 2
    price_y = y + text_height + 30
    
    draw.rectangle([price_x-20, price_y-20, price_x+price_width+20, price_y+price_height+20], fill='white')
    draw.text((price_x, price_y), price_text, fill='green', font=font_small)
    
    # Convert to bytes
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format='JPEG', quality=85)
    img_byte_arr.seek(0)
    
    return img_byte_arr


def generate_images_for_cars():
    """Generate images for all cars that don't have images."""
    cars = Car.objects.all()
    print(f"Generating images for {cars.count()} cars...")
    
    for car in cars:
        # Check if car already has an image (if your Car model has an image field)
        if hasattr(car, 'image') and car.image:
            print(f"Car {car.id} already has an image, skipping...")
            continue
        
        try:
            # Generate image
            img_byte_arr = generate_car_image(car)
            
            # Save to Cloudinary or local media
            # If using Cloudinary
            from cloudinary.uploader import upload
            result = upload(img_byte_arr, 
                           folder='cars/',
                           public_id=f'car_{car.id}',
                           overwrite=True)
            
            # Save the URL to the car's image field
            if hasattr(car, 'image'):
                car.image = result['secure_url']
                car.save()
                print(f"✓ Generated image for {car.brand} {car.model}")
            
        except Exception as e:
            print(f"✗ Error generating image for car {car.id}: {e}")

    print("Done generating images!")


if __name__ == "__main__":
    generate_images_for_cars()