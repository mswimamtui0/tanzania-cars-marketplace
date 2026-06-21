from django.db import models
from django.contrib.auth.models import User
from marketplace.models import CarListing

class ComparisonSet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comparisons')
    cars = models.ManyToManyField(CarListing, related_name='comparisons')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Comparison by {self.user.username} - {self.cars.count()} cars"