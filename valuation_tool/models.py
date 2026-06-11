from django.db import models

from django.contrib.auth.models import User

class ValuationRequest(models.Model):
    CONDITION_CHOICES = [('excellent', 'Excellent'), ('good', 'Good'), ('fair', 'Fair'), ('poor', 'Poor')]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    make = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    year = models.IntegerField()
    mileage = models.IntegerField()
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES)
    estimated_value = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def calculate_value(self):
        base_values = {'Toyota': 25000000, 'Honda': 22000000, 'Nissan': 20000000, 'BMW': 45000000, 'Mercedes': 50000000}
        base = base_values.get(self.make, 18000000)
        age = 2025 - self.year
        depreciation = age * 0.10
        value = base * (1 - depreciation)
        mileage_deduction = (self.mileage / 10000) * 0.02
        value = value * (1 - min(mileage_deduction, 0.30))
        condition_mult = {'excellent': 1.0, 'good': 0.9, 'fair': 0.75, 'poor': 0.6}
        return round(value * condition_mult.get(self.condition, 0.85), -3)
# Create your models here.
