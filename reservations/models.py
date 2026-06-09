from django.db import models
from django.contrib.auth.models import User
from marketplace.models import CarListing

class Reservation(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending Payment'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    )
    
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reservations')
    car = models.ForeignKey(CarListing, on_delete=models.CASCADE)
    reservation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=199.00)
    has_part_exchange = models.BooleanField(default=False)
    part_exchange_car_make = models.CharField(max_length=50, blank=True)
    part_exchange_car_model = models.CharField(max_length=50, blank=True)
    part_exchange_car_year = models.IntegerField(null=True, blank=True)
    part_exchange_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    wants_finance = models.BooleanField(default=False)
    finance_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    delivery_required = models.BooleanField(default=False)
    delivery_address = models.TextField(blank=True)
    delivery_fee = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    reservation_date = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    
    def __str__(self):
        return f"Reservation for {self.car.model} by {self.buyer.username}"

class PartExchangeEvaluation(models.Model):
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE, related_name='evaluations')
    evaluated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='evaluations')
    final_offer = models.DecimalField(max_digits=12, decimal_places=2)
    condition_notes = models.TextField()
    evaluation_date = models.DateTimeField(auto_now_add=True)
    is_accepted = models.BooleanField(default=False)