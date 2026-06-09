from django.db import models
from django.contrib.auth.models import User
from marketplace.models import CarListing

class LeasePlan(models.Model):
    car = models.ForeignKey(CarListing, on_delete=models.CASCADE, related_name='lease_plans')
    contract_months = models.IntegerField(choices=[(24, '24 months'), (36, '36 months'), (48, '48 months'), (60, '60 months')])
    annual_mileage = models.IntegerField(choices=[(5000, '5,000 miles'), (8000, '8,000 miles'), (10000, '10,000 miles'), (12000, '12,000 miles')])
    initial_payment_months = models.IntegerField(choices=[(3, '3 months'), (6, '6 months'), (9, '9 months'), (12, '12 months')], default=6)
    monthly_payment = models.DecimalField(max_digits=10, decimal_places=2)
    total_lease_cost = models.DecimalField(max_digits=12, decimal_places=2)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, default=5.9)
    is_active = models.BooleanField(default=True)
    
    def calculate_initial_payment(self):
        return self.monthly_payment * self.initial_payment_months
    
    def __str__(self):
        return f"{self.car.make} {self.car.model} - {self.contract_months} months"

class LeaseApplication(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lease_applications')
    lease_plan = models.ForeignKey(LeasePlan, on_delete=models.CASCADE)
    employment_status = models.CharField(max_length=50, choices=[('employed','Employed'),('self_employed','Self Employed'),('business','Business Owner')])
    annual_income = models.DecimalField(max_digits=12, decimal_places=2)
    credit_score = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    application_date = models.DateTimeField(auto_now_add=True)
    approval_date = models.DateTimeField(null=True, blank=True)
    documents = models.FileField(upload_to='lease_docs/', blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.lease_plan.car.model} - {self.status}"