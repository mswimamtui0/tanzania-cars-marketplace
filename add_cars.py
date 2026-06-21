import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tanzania_car_marketplace.settings')
django.setup()

from django.contrib.auth.models import User
from marketplace.models import Car

def add_cars():
    # Get or create admin user
    user, created = User.objects.get_or_create(
        username='admin',
        defaults={'email': 'admin@example.com', 'is_staff': True, 'is_superuser': True}
    )
    if created:
        user.set_password('admin123')
        user.save()
        print("✅ Admin user created")
    
    # Sample cars data
    cars_data = [
        {
            'title': 'Toyota Corolla 2020',
            'make': 'Toyota',
            'model': 'Corolla',
            'year': 2020,
            'price': 25000000,
            'mileage': 50000,
            'description': 'Well-maintained Toyota Corolla with full service history. Perfect family car.',
            'fuel_type': 'petrol',
            'transmission': 'automatic',
            'body_type': 'sedan',
            'color': 'White',
            'condition': 'used',
            'featured': True,
            'is_approved': True
        },
        {
            'title': 'Toyota Rav4 2022',
            'make': 'Toyota',
            'model': 'Rav4',
            'year': 2022,
            'price': 35000000,
            'mileage': 30000,
            'description': 'Spacious SUV with excellent off-road capabilities. Great for family adventures.',
            'fuel_type': 'hybrid',
            'transmission': 'automatic',
            'body_type': 'suv',
            'color': 'Blue',
            'condition': 'used',
            'featured': True,
            'is_approved': True
        },
        {
            'title': 'Toyota Harrier 2021',
            'make': 'Toyota',
            'model': 'Harrier',
            'year': 2021,
            'price': 45000000,
            'mileage': 25000,
            'description': 'Luxury SUV with premium features and comfortable interior.',
            'fuel_type': 'petrol',
            'transmission': 'automatic',
            'body_type': 'suv',
            'color': 'Black',
            'condition': 'used',
            'featured': True,
            'is_approved': True
        },
        {
            'title': 'Toyota Land Cruiser V8',
            'make': 'Toyota',
            'model': 'Land Cruiser',
            'year': 2023,
            'price': 85000000,
            'mileage': 10000,
            'description': 'Top-of-the-line Land Cruiser V8. Built for the toughest terrains.',
            'fuel_type': 'diesel',
            'transmission': 'automatic',
            'body_type': 'suv',
            'color': 'Silver',
            'condition': 'new',
            'featured': True,
            'is_approved': True
        },
        {
            'title': 'BMW X5 2022',
            'make': 'BMW',
            'model': 'X5',
            'year': 2022,
            'price': 55000000,
            'mileage': 20000,
            'description': 'German engineering at its finest. Premium SUV with powerful engine.',
            'fuel_type': 'diesel',
            'transmission': 'automatic',
            'body_type': 'suv',
            'color': 'Dark Blue',
            'condition': 'used',
            'featured': True,
            'is_approved': True
        },
        {
            'title': 'Mercedes Benz GLE',
            'make': 'Mercedes',
            'model': 'GLE',
            'year': 2021,
            'price': 60000000,
            'mileage': 18000,
            'description': 'Luxury SUV with Mercedes signature comfort and style.',
            'fuel_type': 'petrol',
            'transmission': 'automatic',
            'body_type': 'suv',
            'color': 'White',
            'condition': 'used',
            'featured': True,
            'is_approved': True
        },
        {
            'title': 'Audi Q7 2020',
            'make': 'Audi',
            'model': 'Q7',
            'year': 2020,
            'price': 40000000,
            'mileage': 35000,
            'description': 'Spacious family SUV with Audi\'s signature Quattro all-wheel drive.',
            'fuel_type': 'petrol',
            'transmission': 'automatic',
            'body_type': 'suv',
            'color': 'Gray',
            'condition': 'used',
            'featured': False,
            'is_approved': True
        },
        {
            'title': 'Honda CR-V 2022',
            'make': 'Honda',
            'model': 'CR-V',
            'year': 2022,
            'price': 32000000,
            'mileage': 15000,
            'description': 'Reliable and fuel-efficient compact SUV. Perfect for city driving.',
            'fuel_type': 'hybrid',
            'transmission': 'automatic',
            'body_type': 'suv',
            'color': 'Red',
            'condition': 'used',
            'featured': False,
            'is_approved': True
        }
    ]

    # Create cars
    count = 0
    for data in cars_data:
        try:
            car = Car.objects.create(
                seller=user,
                title=data['title'],
                make=data['make'],
                model=data['model'],
                year=data['year'],
                price=data['price'],
                mileage=data['mileage'],
                description=data['description'],
                fuel_type=data['fuel_type'],
                transmission=data['transmission'],
                body_type=data['body_type'],
                color=data['color'],
                condition=data['condition'],
                featured=data['featured'],
                is_approved=data['is_approved']
            )
            count += 1
            print(f"✅ Created: {car.title}")
        except Exception as e:
            print(f"❌ Error creating {data['title']}: {e}")

    print(f"\n🎉 Successfully created {count} cars!")
    print(f"📊 Total cars in database: {Car.objects.count()}")

if __name__ == '__main__':
    add_cars()