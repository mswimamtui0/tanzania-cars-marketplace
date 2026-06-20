from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
from cloudinary.models import CloudinaryField

# ========== CORE MODELS ==========

class Car(models.Model):
    """Main Car model for listings."""
    CONDITION_CHOICES = [
        ('new', 'New'),
        ('used', 'Used'),
        ('certified', 'Certified Pre-Owned'),
    ]
    
    FUEL_CHOICES = [
        ('petrol', 'Petrol'),
        ('diesel', 'Diesel'),
        ('electric', 'Electric'),
        ('hybrid', 'Hybrid'),
        ('cng', 'CNG'),
    ]
    
    TRANSMISSION_CHOICES = [
        ('manual', 'Manual'),
        ('automatic', 'Automatic'),
        ('cvt', 'CVT'),
    ]
    
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('sold', 'Sold'),
        ('pending', 'Pending'),
        ('reserved', 'Reserved'),
    ]
    
    # Basic Info
    title = models.CharField(max_length=200)
    brand = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    year = models.IntegerField()
    price = models.DecimalField(max_digits=15, decimal_places=2)
    mileage = models.IntegerField(help_text="Mileage in kilometers")
    
    # Details
    fuel_type = models.CharField(max_length=20, choices=FUEL_CHOICES)
    transmission = models.CharField(max_length=20, choices=TRANSMISSION_CHOICES)
    color = models.CharField(max_length=50)
    description = models.TextField()
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default='used')
    location = models.CharField(max_length=200)
    
    # Images
    image = CloudinaryField('image', null=True, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    is_featured = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    
    # Relationships
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cars')
    dealer = models.ForeignKey('Dealer', on_delete=models.SET_NULL, null=True, blank=True, related_name='cars')
    yard = models.ForeignKey('Yard', on_delete=models.SET_NULL, null=True, blank=True, related_name='cars')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.brand} {self.model} ({self.year})"
    
    def get_absolute_url(self):
        return reverse('car_detail', args=[str(self.id)])
    
    @property
    def is_sold(self):
        return self.status == 'sold'


class CarImage(models.Model):
    """Additional images for cars."""
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='images')
    image = CloudinaryField('image')
    caption = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-is_primary', 'created_at']
    
    def __str__(self):
        return f"Image for {self.car.title}"


class Dealer(models.Model):
    """Dealer model for car sellers."""
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
    
    class Meta:
        ordering = ['business_name']
    
    def __str__(self):
        return self.business_name


class Yard(models.Model):
    """Physical yard location for car storage."""
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    capacity = models.IntegerField()
    is_active = models.BooleanField(default=True)
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='managed_yards')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


class YardDealerAssignment(models.Model):
    """Assignment of dealers to yards."""
    dealer = models.ForeignKey(Dealer, on_delete=models.CASCADE, related_name='yard_assignments')
    yard = models.ForeignKey(Yard, on_delete=models.CASCADE, related_name='dealer_assignments')
    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='assigned_dealers')
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('dealer', 'yard')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.dealer.business_name} @ {self.yard.name}"


class DealerAssignment(models.Model):
    """Assignment of cars to dealers."""
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='dealer_assignments')
    dealer = models.ForeignKey(Dealer, on_delete=models.CASCADE, related_name='car_assignments')
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=5.00)
    is_active = models.BooleanField(default=True)
    assigned_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('car', 'dealer')
        ordering = ['-assigned_at']
    
    def __str__(self):
        return f"{self.car.title} - {self.dealer.business_name}"


# ========== FAVORITES ==========

class Favorite(models.Model):
    """Model for user favorites."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'car')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.car.title}"


# ========== REVIEWS ==========

class Review(models.Model):
    """Reviews for cars and dealers."""
    RATING_CHOICES = [(i, f"{i} Stars") for i in range(1, 6)]
    
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='reviews', null=True, blank=True)
    dealer = models.ForeignKey(Dealer, on_delete=models.CASCADE, related_name='reviews', null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(choices=RATING_CHOICES)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.rating} stars"


# ========== REPORTS ==========

class Report(models.Model):
    """Model for reporting issues with listings."""
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

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.reason} - {self.car.title}"


# ========== MESSAGES ==========

class Message(models.Model):
    """Model for user-to-user messages."""
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    car = models.ForeignKey(Car, on_delete=models.CASCADE, null=True, blank=True, related_name='messages')
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    parent_message = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.sender.username} -> {self.recipient.username}: {self.content[:30]}..."


# ========== INSPECTIONS ==========

class InspectionRequest(models.Model):
    """Vehicle inspection requests."""
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
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Inspection for {self.car.title} - {self.status}"


# ========== LISTING PACKAGES ==========

class ListingPackage(models.Model):
    """Listing packages for car advertisements."""
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_days = models.IntegerField()
    is_featured = models.BooleanField(default=False)
    is_premium = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['price']
    
    def __str__(self):
        return self.name