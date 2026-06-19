from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# ========== USER PROFILE ==========
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

# ========== CAR YARD ==========
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

# ========== CAR LISTING ==========
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

# ========== WISHLIST ==========
class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist_items')
    car = models.ForeignKey(CarListing, on_delete=models.CASCADE, related_name='wishlisted_by')
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'car')
    
    def __str__(self):
        return f"{self.user.username} - {self.car}"

# ========== COMPARISON SET ==========
class ComparisonSet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='comparison_set')
    cars = models.ManyToManyField(CarListing, related_name='in_comparisons')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username}'s comparison"

# ========== SOLD REQUEST ==========
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

# ========== RESERVATION ==========
class Reservation(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    )
    
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reservations')
    car = models.ForeignKey(CarListing, on_delete=models.CASCADE, related_name='reservations')
    reservation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=50000)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.buyer.username} - {self.car.make} {self.car.model}"

# ========== INSPECTION REQUEST ==========
class InspectionRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    
    car = models.ForeignKey(CarListing, on_delete=models.CASCADE, related_name='inspections')
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='inspections')
    inspection_date = models.DateTimeField(null=True, blank=True)
    location = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    fee = models.DecimalField(max_digits=10, decimal_places=2, default=50000)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Inspection for {self.car.make} {self.car.model} by {self.buyer.username}"

# ========== YARD DEALER ASSIGNMENT ==========
# ONLY ONE DEFINITION - KEEP THIS ONE
class YardDealerAssignment(models.Model):
    """Yard manager assigns dealers to their yard"""
    yard = models.ForeignKey(CarYard, on_delete=models.CASCADE, related_name='assigned_dealers')
    dealer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assigned_yards')
    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='dealer_assignments')
    is_active = models.BooleanField(default=True)
    assigned_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        unique_together = ('yard', 'dealer')
    
    def __str__(self):
        return f"{self.dealer.username} assigned to {self.yard.name}"

# ========== DEALER COMMISSION ==========
class DealerCommission(models.Model):
    """Track dealer commissions"""
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
    )
    
    dealer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='commissions')
    car = models.ForeignKey(CarListing, on_delete=models.CASCADE)
    sale_amount = models.DecimalField(max_digits=12, decimal_places=2)
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=2.0)
    commission_amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.dealer.username} - {self.commission_amount} - {self.status}"

# ========== FAKE LISTING REPORT ==========
class FakeListingReport(models.Model):
    """Report fake or suspicious listings"""
    STATUS_CHOICES = (
        ('pending', 'Pending Review'),
        ('investigating', 'Under Investigation'),
        ('resolved', 'Resolved'),
        ('dismissed', 'Dismissed'),
    )
    
    REASON_CHOICES = (
        ('fake_car', 'Fake/Non-existent car'),
        ('wrong_price', 'Misleading price'),
        ('stolen_car', 'Suspected stolen vehicle'),
        ('scam', 'Scam attempt'),
        ('other', 'Other'),
    )
    
    car = models.ForeignKey(CarListing, on_delete=models.CASCADE, related_name='reports')
    reported_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports')
    reason = models.CharField(max_length=20, choices=REASON_CHOICES)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    admin_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Report on {self.car} by {self.reported_by.username}"