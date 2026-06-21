from django.db import models
from django.contrib.auth.models import User
from marketplace.models import CarListing

class Conversation(models.Model):
    """Chat conversation between users"""
    participants = models.ManyToManyField(User, related_name='conversations')
    car = models.ForeignKey(CarListing, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Conversation between {', '.join([u.username for u in self.participants.all()])}"

class Message(models.Model):
    """Individual message in a conversation"""
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Message from {self.sender.username} at {self.created_at}"

class DealerVerificationRequest(models.Model):
    """Yard Manager verifies dealers"""
    STATUS_CHOICES = (
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    
    dealer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='verification_requests')
    yard_manager = models.ForeignKey(User, on_delete=models.CASCADE, related_name='verifications_given')
    business_license = models.FileField(upload_to='licenses/')
    tin_number = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.dealer.username} - {self.status}"

class EscalationReport(models.Model):
    """Buyer escalates when dealer unresponsive"""
    REASON_CHOICES = (
        ('no_response', 'Dealer not responding'),
        ('misleading_info', 'Misleading car information'),
        ('payment_issue', 'Payment problem'),
        ('other', 'Other'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'Pending Admin Review'),
        ('investigating', 'Under Investigation'),
        ('resolved', 'Resolved'),
        ('dismissed', 'Dismissed'),
    )
    
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='escalations_made')
    dealer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='escalations_received')
    car = models.ForeignKey(CarListing, on_delete=models.CASCADE, null=True, blank=True)
    reason = models.CharField(max_length=50, choices=REASON_CHOICES)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    admin_response = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Escalation: {self.buyer.username} vs {self.dealer.username}"

class WhatsAppIntegration(models.Model):
    """Store dealer WhatsApp numbers"""
    dealer = models.OneToOneField(User, on_delete=models.CASCADE, related_name='whatsapp_settings')
    whatsapp_number = models.CharField(max_length=20, help_text="Include country code")
    is_verified = models.BooleanField(default=False)
    auto_reply_message = models.TextField(default="Thank you for your inquiry! I'll respond shortly.")
    
    def __str__(self):
        return f"{self.dealer.username}: {self.whatsapp_number}"
    
    # Add to existing communication/models.py

class Escalation(models.Model):
    """Complete escalation tracking system"""
    ESCALATION_LEVEL_CHOICES = (
        ('level_1', 'Level 1: Dealer Unresponsive'),
        ('level_2', 'Level 2: Yard Manager介入'),
        ('level_3', 'Level 3: Admin Final Resolution'),
    )
    
    STATUS_CHOICES = (
        ('pending_dealer', 'Waiting for Dealer Response'),
        ('escalated_yard', 'Escalated to Yard Manager'),
        ('yard_investigating', 'Yard Manager Investigating'),
        ('escalated_admin', 'Escalated to Admin'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    )
    
    RESOLUTION_CHOICES = (
        ('refund', 'Refund Issued'),
        ('dealer_warning', 'Dealer Warning Issued'),
        ('dealer_suspended', 'Dealer Suspended'),
        ('dealer_removed', 'Dealer Removed'),
        ('compensation', 'Buyer Compensation'),
        ('explanation', 'Explanation Provided'),
        ('other', 'Other Resolution'),
    )
    
    # Parties involved
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='escalations_as_buyer')
    dealer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='escalations_as_dealer')
    yard_manager = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='escalations_as_yard')
    admin = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='escalations_as_admin')
    
    # Escalation details
    car = models.ForeignKey('marketplace.CarListing', on_delete=models.CASCADE, null=True, blank=True)
    reservation = models.ForeignKey('reservations.Reservation', on_delete=models.CASCADE, null=True, blank=True)
    
    reason = models.CharField(max_length=100, choices=[
        ('no_response', 'Dealer not responding after 48 hours'),
        ('wrong_car', 'Car not as described'),
        ('payment_issue', 'Payment not processed'),
        ('delivery_issue', 'Delivery problem'),
        ('document_issue', 'Documentation problem'),
        ('other', 'Other issue'),
    ])
    
    description = models.TextField()
    evidence = models.FileField(upload_to='escalation_evidence/', null=True, blank=True)
    
    # Escalation tracking
    current_level = models.CharField(max_length=20, choices=ESCALATION_LEVEL_CHOICES, default='level_1')
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='pending_dealer')
    
    # Timelines
    created_at = models.DateTimeField(auto_now_add=True)
    dealer_notified_at = models.DateTimeField(null=True, blank=True)
    dealer_deadline = models.DateTimeField(null=True, blank=True)
    escalated_to_yard_at = models.DateTimeField(null=True, blank=True)
    escalated_to_admin_at = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    # Resolutions
    resolution_type = models.CharField(max_length=30, choices=RESOLUTION_CHOICES, null=True, blank=True)
    resolution_notes = models.TextField(blank=True)
    action_taken_against_dealer = models.TextField(blank=True)
    compensation_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    def __str__(self):
        return f"Escalation #{self.id}: {self.buyer.username} vs {self.dealer.username}"
    
    def can_escalate_to_yard(self):
        """Check if escalation can go to yard manager"""
        return self.status == 'pending_dealer' and self.current_level == 'level_1'
    
    def can_escalate_to_admin(self):
        """Check if escalation can go to admin"""
        return self.status in ['yard_investigating', 'escalated_yard'] and self.current_level == 'level_2'

class EscalationComment(models.Model):
    """Comments and updates on escalations"""
    escalation = models.ForeignKey(Escalation, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField()
    is_internal = models.BooleanField(default=False, help_text="Internal note (not visible to buyer)")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Comment on #{self.escalation.id} by {self.author.username}"

class YardManagerAssignment(models.Model):
    """Assign yard managers to dealers"""
    yard_manager = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assigned_dealers')
    dealer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assigned_yard_manager')
    assigned_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ('yard_manager', 'dealer')
    
    def __str__(self):
        return f"{self.yard_manager.username} → {self.dealer.username}"