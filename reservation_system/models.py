from django.db import models
from django.contrib.auth.models import User
from marketplace.models import CarListing

class Reservation(models.Model):
    STATUS_CHOICES = [('pending', 'Pending'), ('confirmed', 'Confirmed'), ('cancelled', 'Cancelled'), ('completed', 'Completed')]
    
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reservations')
    car = models.ForeignKey(CarListing, on_delete=models.CASCADE, related_name='reservations')
    reservation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=50000)
    has_part_exchange = models.BooleanField(default=False)
    part_exchange_car = models.TextField(blank=True)
    wants_finance = models.BooleanField(default=False)
    finance_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    delivery_required = models.BooleanField(default=False)
    delivery_address = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    
    def __str__(self):
        return f"Reservation for {self.car.model} by {self.buyer.username}"