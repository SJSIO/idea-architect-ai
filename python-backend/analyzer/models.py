from django.db import models
import uuid


class Project(models.Model):
    """Model to store startup analysis projects."""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('analyzing', 'Analyzing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    startup_idea = models.TextField()
    target_market = models.TextField(blank=True, null=True)
    
    # Analysis results
    market_analysis = models.TextField(blank=True, null=True)
    cost_prediction = models.TextField(blank=True, null=True)
    business_strategy = models.TextField(blank=True, null=True)
    monetization = models.TextField(blank=True, null=True)
    legal_considerations = models.TextField(blank=True, null=True)
    tech_stack = models.TextField(blank=True, null=True)
    strategist_critique = models.TextField(blank=True, null=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.startup_idea[:50]}... ({self.status})"
