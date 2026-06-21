from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
from cloudinary.models import CloudinaryField


# ========================================
# USER PROFILE MODEL
# ========================================

class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('dealer', 'Dealer'),
        ('yard_manager', 'Yard Manager'),
        ('buyer', 'Buyer'),
    ]
    
    VERIFICATION_CHOICES = [
        (1, 'Level 1 - Unverified'),
        (2, 'Level 2 - Partially Verified'),
        (3, 'Level 3 - Fully Verified'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userprofile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='buyer')
    phone = models.CharField(max_length=15, blank=True)
    email_verified = models.BooleanField(default=False)
    verification_level = models.IntegerField(choices=VERIFICATION_CHOICES, default=1)
    id_uploaded = models.BooleanField(default=False)
    location_verified = models.BooleanField(default=False)
    verified_badge = models.BooleanField(default=False)
    company_name = models.CharField(max_length=200, blank=True)
    whatsapp_number = models.CharField(max_length=15, blank=True)
    location = models.CharField(max_length=200, blank=True)
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    total_sales = models.IntegerField(default=0)
    total_commission = models.DecimalField(max_digits=15, decimal_places=2, default=0.0)
    is_active_agent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.role}"
    
    class Meta:
        ordering = ['-created_at']


# ========================================
# CAR MODEL
# ========================================

class Car(models.Model):
    FUEL_CHOICES = [
        ('petrol', 'Petrol'),
        ('diesel', 'Diesel'),
        ('electric', 'Electric'),
        ('hybrid', 'Hybrid'),
    ]
    
    TRANSMISSION_CHOICES = [
        ('manual', 'Manual'),
        ('automatic', 'Automatic'),
    ]
    
    BODY_CHOICES = [
        ('sedan', 'Sedan'),
        ('suv', 'SUV'),
        ('truck', 'Truck'),
        ('van', 'Van'),
        ('hatchback', 'Hatchback'),
        ('coupe', 'Coupe'),
        ('convertible', 'Convertible'),
    ]
    
    CONDITION_CHOICES = [
        ('new', 'New'),
        ('used', 'Used'),
        ('certified', 'Certified'),
    ]
    
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('sold', 'Sold'),
        ('pending', 'Pending'),
        ('reserved', 'Reserved'),
    ]
    
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cars')
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=15, decimal_places=2)
    year = models.IntegerField()
    make = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    mileage = models.IntegerField()
    fuel_type = models.CharField(max_length=20, choices=FUEL_CHOICES)
    transmission = models.CharField(max_length=20, choices=TRANSMISSION_CHOICES)
    body_type = models.CharField(max_length=20, choices=BODY_CHOICES)
    color = models.CharField(max_length=30)
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    images = models.ImageField(upload_to='cars/', null=True, blank=True)
    video_url = models.URLField(blank=True, null=True)
    featured = models.BooleanField(default=False)
    is_negotiable = models.BooleanField(default=True)
    is_approved = models.BooleanField(default=False)
    is_sold = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.title} ({self.year})"
    
    def get_absolute_url(self):
        return reverse('car_detail', args=[str(self.id)])
    
    class Meta:
        ordering = ['-created_at']


# ========================================
# CAR IMAGE MODEL
# ========================================

class CarImage(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='car_images')
    image = models.ImageField(upload_to='cars/')
    caption = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Image for {self.car.title}"
    
    class Meta:
        ordering = ['-is_primary', 'created_at']


# ========================================
# CAR LISTING MODEL (Legacy - Keep for compatibility)
# ========================================

class CarListing(models.Model):
    FUEL_CHOICES = [
        ('petrol', 'Petrol'),
        ('diesel', 'Diesel'),
        ('electric', 'Electric'),
        ('hybrid', 'Hybrid'),
    ]
    
    TRANSMISSION_CHOICES = [
        ('manual', 'Manual'),
        ('automatic', 'Automatic'),
    ]
    
    BODY_CHOICES = [
        ('sedan', 'Sedan'),
        ('suv', 'SUV'),
        ('truck', 'Truck'),
        ('van', 'Van'),
        ('hatchback', 'Hatchback'),
        ('coupe', 'Coupe'),
        ('convertible', 'Convertible'),
    ]
    
    CONDITION_CHOICES = [
        ('new', 'New'),
        ('used', 'Used'),
        ('certified', 'Certified'),
    ]
    
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='listings')
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=15, decimal_places=2)
    year = models.IntegerField()
    make = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    mileage = models.IntegerField()
    fuel_type = models.CharField(max_length=20, choices=FUEL_CHOICES)
    transmission = models.CharField(max_length=20, choices=TRANSMISSION_CHOICES)
    body_type = models.CharField(max_length=20, choices=BODY_CHOICES)
    color = models.CharField(max_length=30)
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES)
    images = models.ImageField(upload_to='cars/', null=True, blank=True)
    video_url = models.URLField(blank=True, null=True)
    featured = models.BooleanField(default=False)
    is_negotiable = models.BooleanField(default=True)
    is_approved = models.BooleanField(default=False)
    is_sold = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.title} ({self.year})"
    
    def get_absolute_url(self):
        return reverse('car_detail', args=[str(self.id)])
    
    class Meta:
        ordering = ['-created_at']


# ========================================
# DEALER MODEL
# ========================================

class Dealer(models.Model):
    VERIFICATION_LEVELS = [
        ('1', 'Level 1 - Basic'),
        ('2', 'Level 2 - Verified'),
        ('3', 'Level 3 - Premium'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='dealer_profile')
    business_name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    phone = models.CharField(max_length=20)
    location = models.CharField(max_length=200)
    website = models.URLField(blank=True)
    verification_level = models.CharField(max_length=1, choices=VERIFICATION_LEVELS, default='1')
    is_verified = models.BooleanField(default=False)
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=5.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.business_name
    
    class Meta:
        ordering = ['business_name']


# ========================================
# YARD MODEL
# ========================================

class Yard(models.Model):
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    capacity = models.IntegerField()
    is_active = models.BooleanField(default=True)
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='managed_yards')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']


# ========================================
# YARD DEALER ASSIGNMENT MODEL
# ========================================

class YardDealerAssignment(models.Model):
    dealer = models.ForeignKey(Dealer, on_delete=models.CASCADE, related_name='yard_assignments')
    yard = models.ForeignKey(Yard, on_delete=models.CASCADE, related_name='dealer_assignments')
    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='assigned_dealers')
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.dealer.business_name} @ {self.yard.name}"
    
    class Meta:
        unique_together = ('dealer', 'yard')
        ordering = ['-created_at']


# ========================================
# DEALER ASSIGNMENT MODEL
# ========================================

class DealerAssignment(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='dealer_assignments')
    dealer = models.ForeignKey(Dealer, on_delete=models.CASCADE, related_name='car_assignments')
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=5.00)
    is_active = models.BooleanField(default=True)
    assigned_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.car.title} - {self.dealer.business_name}"
    
    class Meta:
        unique_together = ('car', 'dealer')
        ordering = ['-assigned_at']


# ========================================
# FAVORITE MODEL
# ========================================

class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.car.title}"
    
    class Meta:
        unique_together = ('user', 'car')
        ordering = ['-created_at']


# ========================================
# REVIEW MODEL
# ========================================

class Review(models.Model):
    RATING_CHOICES = [(i, f"{i} Stars") for i in range(1, 6)]
    
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='reviews', null=True, blank=True)
    dealer = models.ForeignKey(Dealer, on_delete=models.CASCADE, related_name='reviews', null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(choices=RATING_CHOICES)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.rating} stars"
    
    class Meta:
        ordering = ['-created_at']


# ========================================
# REPORT MODEL
# ========================================

class Report(models.Model):
    REASON_CHOICES = [
        ('fake', 'Fake Listing'),
        ('fraud', 'Fraud/Scam'),
        ('duplicate', 'Duplicate Listing'),
        ('price_misleading', 'Misleading Price'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('investigating', 'Under Investigation'),
        ('resolved', 'Resolved'),
        ('dismissed', 'Dismissed'),
    ]
    
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='reports')
    reported_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports')
    reason = models.CharField(max_length=50, choices=REASON_CHOICES)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='resolved_reports')
    resolution_notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.reason} - {self.car.title}"
    
    class Meta:
        ordering = ['-created_at']


# ========================================
# MESSAGE MODEL
# ========================================

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    car = models.ForeignKey(Car, on_delete=models.CASCADE, null=True, blank=True, related_name='messages')
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    parent_message = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    
    def __str__(self):
        return f"{self.sender.username} -> {self.recipient.username}: {self.content[:30]}..."
    
    class Meta:
        ordering = ['created_at']


# ========================================
# INSPECTION REQUEST MODEL
# ========================================

class InspectionRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='inspections')
    requested_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='inspection_requests')
    scheduled_date = models.DateTimeField()
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    inspection_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='completed_inspections')
    inspection_report = models.TextField(blank=True)
    
    def __str__(self):
        return f"Inspection for {self.car.title} - {self.status}"
    
    class Meta:
        ordering = ['-created_at']


# ========================================
# LISTING PACKAGE MODEL
# ========================================

class ListingPackage(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_days = models.IntegerField()
    is_featured = models.BooleanField(default=False)
    is_premium = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['price']