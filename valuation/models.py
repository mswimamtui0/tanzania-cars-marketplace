from django.db import models
from django.contrib.auth.models import User
from marketplace.models import CarListing

class ValuationRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='valuations')
    make = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    year = models.IntegerField()
    mileage = models.IntegerField()
    condition = models.CharField(max_length=20, choices=[('excellent','Excellent'),('good','Good'),('fair','Fair'),('poor','Poor')])
    estimated_value = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    market_demand = models.CharField(max_length=20, choices=[('high','High'),('medium','Medium'),('low','Low')], null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def calculate_valuation(self):
        # Base value calculation
        base_value = 0
        if self.make == 'Toyota':
            base_value = 25000
        elif self.make == 'Honda':
            base_value = 22000
        elif self.make == 'Nissan':
            base_value = 20000
        else:
            base_value = 18000
        
        # Depreciation by year
        current_year = 2025
        age = current_year - self.year
        depreciation = age * 0.10  # 10% per year
        value_after_age = base_value * (1 - depreciation)
        
        # Mileage deduction
        mileage_deduction = (self.mileage / 10000) * 0.05  # 5% per 10,000 km
        value_after_mileage = value_after_age * (1 - min(mileage_deduction, 0.30))
        
        # Condition multiplier
        condition_multiplier = {'excellent': 1.0, 'good': 0.9, 'fair': 0.75, 'poor': 0.6}
        final_value = value_after_mileage * condition_multiplier[self.condition]
        
        return round(final_value, 2)

class InstantOffer(models.Model):
    valuation = models.ForeignKey(ValuationRequest, on_delete=models.CASCADE)
    dealer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='instant_offers')
    offer_amount = models.DecimalField(max_digits=12, decimal_places=2)
    expires_at = models.DateTimeField()
    is_accepted = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Offer from {self.dealer.username}: ${self.offer_amount}"