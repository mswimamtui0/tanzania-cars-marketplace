from django.db import models
from django.db import models
from django.contrib.auth.models import User
from marketplace.models import CarListing

class LeasePlan(models.Model):
    TERM_CHOICES = [(24, '24 months'), (36, '36 months'), (48, '48 months'), (60, '60 months')]
    MILEAGE_CHOICES = [(5000, '5,000 km/year'), (10000, '10,000 km/year'), (15000, '15,000 km/year'), (20000, '20,000 km/year')]
    
    car = models.ForeignKey(CarListing, on_delete=models.CASCADE, related_name='lease_plans')
    term_months = models.IntegerField(choices=TERM_CHOICES, default=36)
    annual_mileage = models.IntegerField(choices=MILEAGE_CHOICES, default=10000)
    monthly_payment = models.DecimalField(max_digits=12, decimal_places=2)
    initial_payment = models.DecimalField(max_digits=12, decimal_places=2)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, default=5.9)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.car.make} {self.car.model} - {self.term_months} months"

class LeaseApplication(models.Model):
    STATUS_CHOICES = [('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected'), ('completed', 'Completed')]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lease_applications')
    lease_plan = models.ForeignKey(LeasePlan, on_delete=models.CASCADE)
    employment_status = models.CharField(max_length=50)
    annual_income = models.DecimalField(max_digits=12, decimal_places=2)
    credit_score = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.lease_plan.car.model} - {self.status}"
# Create your models here.
