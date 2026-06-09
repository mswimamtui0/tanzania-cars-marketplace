from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    ROLE_CHOICES = (
        ('buyer', 'Buyer'),
        ('seller', 'Seller'),
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
    
    # Seller specific fields
    verification_level = models.IntegerField(choices=VERIFICATION_LEVELS, default=1)
    id_uploaded = models.FileField(upload_to='ids/', blank=True, null=True)
    location_verified = models.BooleanField(default=False)
    verified_badge = models.BooleanField(default=False)
    company_name = models.CharField(max_length=100, blank=True)
    
    # Agent specific fields
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=2.0)
    total_sales = models.IntegerField(default=0)
    total_commission = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_active_agent = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.role} - Level {self.verification_level}"


# ========== ADD THIS CarYard MODEL ==========
class CarYard(models.Model):
    """Car yard/physical location model"""
    name = models.CharField(max_length=100)
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='managed_yards')
    location = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    description = models.TextField(blank=True)
    phone = models.CharField(max_length=15, blank=True)
    email = models.EmailField(blank=True)
    opening_hours = models.TextField(blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    total_reviews = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {self.city}"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


class CarListing(models.Model):
    LISTING_PACKAGES = (
        ('normal', 'Normal - TZS 10,000'),
        ('featured', 'Featured - TZS 50,000'),
        ('premium', 'Premium - TZS 100,000'),
    )
    
    CONDITION_CHOICES = (
        ('new', 'New'),
        ('used', 'Used'),
    )
    
    TRANSMISSION_CHOICES = (
        ('manual', 'Manual'),
        ('automatic', 'Automatic'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('sold', 'Sold'),
        ('rejected', 'Rejected'),
    )
    
    FUEL_CHOICES = (
        ('petrol', 'Petrol'),
        ('diesel', 'Diesel'),
        ('electric', 'Electric'),
        ('hybrid', 'Hybrid'),
    )
    
    # Car details
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
    
    # Seller and verification
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='listings', null=True, blank=True)
    yard = models.ForeignKey(CarYard, on_delete=models.SET_NULL, null=True, blank=True, related_name='cars')
    verification_level_required = models.IntegerField(default=1)
    
    # Listing package
    package = models.CharField(max_length=20, choices=LISTING_PACKAGES, default='normal')
    payment_made = models.BooleanField(default=False)
    payment_confirmed = models.BooleanField(default=False)
    
    # Agent assignment
    assigned_agent = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_listings')
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    is_featured = models.BooleanField(default=False)
    views_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='approved_listings')
    approved_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.year} {self.make} {self.model}"


class ChatSession(models.Model):
    """Track WhatsApp chat sessions"""
    CHAT_ROUTES = (
        ('agent', 'Routed to Agent'),
        ('seller', 'Direct to Seller'),
        ('admin', 'Admin Review'),
    )
    
    car = models.ForeignKey(CarListing, on_delete=models.CASCADE, related_name='chats')
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='buyer_chats', null=True, blank=True)
    buyer_name = models.CharField(max_length=100, blank=True)
    buyer_phone = models.CharField(max_length=20, blank=True)
    route_to = models.CharField(max_length=20, choices=CHAT_ROUTES, default='agent')
    assigned_agent = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='assigned_chats')
    seller_introduced = models.BooleanField(default=False)
    inspection_scheduled = models.BooleanField(default=False)
    deal_closed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Chat for {self.car} - {self.route_to}"


class InspectionRequest(models.Model):
    """Inspection service requests"""
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
    inspector_name = models.CharField(max_length=100, blank=True)
    inspector_phone = models.CharField(max_length=20, blank=True)
    report = models.FileField(upload_to='inspection_reports/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    fee = models.DecimalField(max_digits=10, decimal_places=2, default=50000)
    payment_made = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Inspection for {self.car} - {self.status}"


class Payment(models.Model):
    """Track payments for listings and services"""
    PAYMENT_TYPES = (
        ('listing_normal', 'Normal Listing'),
        ('listing_featured', 'Featured Listing'),
        ('listing_premium', 'Premium Listing'),
        ('inspection', 'Inspection Service'),
        ('commission', 'Agent Commission'),
    )
    
    PAYMENT_METHODS = (
        ('mpesa', 'M-Pesa'),
        ('cash', 'Cash'),
        ('bank', 'Bank Transfer'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    car_listing = models.ForeignKey(CarListing, on_delete=models.CASCADE, null=True, blank=True)
    inspection = models.ForeignKey(InspectionRequest, on_delete=models.CASCADE, null=True, blank=True)
    payment_type = models.CharField(max_length=30, choices=PAYMENT_TYPES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    mpesa_receipt = models.CharField(max_length=50, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.payment_type} - {self.amount}"


class AgentCommission(models.Model):
    """Track agent commissions"""
    agent = models.ForeignKey(User, on_delete=models.CASCADE, related_name='commissions')
    car = models.ForeignKey(CarListing, on_delete=models.CASCADE)
    sale_amount = models.DecimalField(max_digits=12, decimal_places=2)
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2)
    commission_amount = models.DecimalField(max_digits=12, decimal_places=2)
    paid = models.BooleanField(default=False)
    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.agent.username} - {self.commission_amount} for {self.car}"