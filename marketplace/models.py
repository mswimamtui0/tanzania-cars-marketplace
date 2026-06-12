from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    ROLE_CHOICES = (
        ('buyer', 'Buyer'),
        ('dealer', 'Dealer'),
        ('yard_manager', 'Yard Manager'),
        ('agent', 'Agent/Broker'),
        ('admin', 'Admin'),
    )
    
    VERIFICATION_LEVELS = (
        (1, 'Level 1 - Unverified (Phone only)'),
        (2, 'Level 2 - Partially Verified (ID uploaded)'),
        (3, 'Level 3 - Fully Verified (ID + Location verified)'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='buyer')
    phone = models.CharField(max_length=15, blank=True, null=True)
    email_verified = models.BooleanField(default=False)
    verification_level = models.IntegerField(choices=VERIFICATION_LEVELS, default=1)
    id_uploaded = models.FileField(upload_to='ids/', blank=True, null=True)
    location_verified = models.BooleanField(default=False)
    verified_badge = models.BooleanField(default=False)
    company_name = models.CharField(max_length=100, blank=True)
    whatsapp_number = models.CharField(max_length=20, blank=True, null=True)
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=2.0)
    total_sales = models.IntegerField(default=0)
    total_commission = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_active_agent = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.role}"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

class CarYard(models.Model):
    name = models.CharField(max_length=100)
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='managed_yards')
    location = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    phone = models.CharField(max_length=15, blank=True)
    email = models.EmailField(blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {self.city}"

class CarListing(models.Model):
    LISTING_PACKAGES = (
        ('normal', 'Normal - TZS 10,000'),
        ('featured', 'Featured - TZS 50,000'),
        ('premium', 'Premium - TZS 100,000'),
    )
    CONDITION_CHOICES = (('new', 'New'), ('used', 'Used'))
    TRANSMISSION_CHOICES = (('manual', 'Manual'), ('automatic', 'Automatic'))
    STATUS_CHOICES = (('pending', 'Pending'), ('approved', 'Approved'), ('sold', 'Sold'), ('rejected', 'Rejected'))
    FUEL_CHOICES = (('petrol', 'Petrol'), ('diesel', 'Diesel'), ('electric', 'Electric'), ('hybrid', 'Hybrid'))
    
    title = models.CharField(max_length=200)
    make = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    year = models.IntegerField()
    price = models.DecimalField(max_digits=12, decimal_places=2)
    mileage = models.IntegerField()
    condition = models.CharField(max_length=10, choices=CONDITION_CHOICES, default='used')
    transmission = models.CharField(max_length=10, choices=TRANSMISSION_CHOICES, default='manual')
    fuel_type = models.CharField(max_length=20, choices=FUEL_CHOICES, default='petrol')
    description = models.TextField(blank=True)
    images = models.ImageField(upload_to='cars/', blank=True, null=True)
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='listings', null=True, blank=True)
    yard = models.ForeignKey(CarYard, on_delete=models.SET_NULL, null=True, blank=True, related_name='cars')
    package = models.CharField(max_length=20, choices=LISTING_PACKAGES, default='normal')
    payment_made = models.BooleanField(default=False)
    payment_confirmed = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    is_featured = models.BooleanField(default=False)
    views_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.year} {self.make} {self.model}"

class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist_items')
    car = models.ForeignKey(CarListing, on_delete=models.CASCADE, related_name='wishlisted_by')
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'car')
    
    def __str__(self):
        return f"{self.user.username} - {self.car}"

class ComparisonSet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='comparison_set')
    cars = models.ManyToManyField(CarListing, related_name='in_comparisons')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username}'s comparison"

class SoldRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending Dealer Approval'),
        ('approved', 'Approved - Car Sold'),
        ('rejected', 'Rejected'),
    )
    
    car = models.ForeignKey(CarListing, on_delete=models.CASCADE, related_name='sold_requests')
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sold_requests')
    dealer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='dealer_sold_requests')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    buyer_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.buyer.username} bought {self.car.make} {self.car.model} - {self.status}"
    
    # Add these after your existing models

class Reservation(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    )
    
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reservations')
    car = models.ForeignKey('CarListing', on_delete=models.CASCADE, related_name='reservations')
    reservation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=50000)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.buyer.username} - {self.car.make} {self.car.model}"

class InspectionRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    
    car = models.ForeignKey('CarListing', on_delete=models.CASCADE, related_name='inspections')
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='inspections')
    inspection_date = models.DateTimeField(null=True, blank=True)
    location = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    fee = models.DecimalField(max_digits=10, decimal_places=2, default=50000)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Inspection for {self.car.make} {self.car.model} by {self.buyer.username}"