from django.db import models
from django.contrib.auth.models import User
from marketplace.models import CarListing, CarYard

class Review(models.Model):
    RATING_CHOICES = [(i, i) for i in range(1, 6)]
    
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_given')
    car = models.ForeignKey(CarListing, on_delete=models.CASCADE, null=True, blank=True, related_name='reviews')
    dealer = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='reviews_received')
    yard = models.ForeignKey(CarYard, on_delete=models.CASCADE, null=True, blank=True, related_name='reviews')
    rating = models.IntegerField(choices=RATING_CHOICES)
    title = models.CharField(max_length=200)
    comment = models.TextField()
    pros = models.TextField(blank=True)
    cons = models.TextField(blank=True)
    verified_purchase = models.BooleanField(default=False)
    helpful_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('reviewer', 'car', 'dealer', 'yard')
    
    def __str__(self):
        return f"{self.reviewer.username} rated {self.rating} stars"

class HelpfulVote(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='votes')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_helpful = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('review', 'user')