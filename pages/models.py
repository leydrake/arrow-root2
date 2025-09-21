from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.

class AdminProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_admin = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - Admin Profile"

class Visit(models.Model):
    """Track user visits to the site"""
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True, null=True)
    page_url = models.URLField()
    referer = models.URLField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField(default=timezone.now)
    session_id = models.CharField(max_length=100, blank=True, null=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"Visit from {self.ip_address} at {self.timestamp.strftime('%Y-%m-%d %H:%M')}"

class Download(models.Model):
    """Track file downloads"""
    file_name = models.CharField(max_length=255)
    file_path = models.CharField(max_length=500)
    file_size = models.BigIntegerField(default=0)  # in bytes
    download_count = models.PositiveIntegerField(default=0)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    ip_address = models.GenericIPAddressField(default='127.0.0.1')
    user_agent = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(default=timezone.now)
    session_id = models.CharField(max_length=100, blank=True, null=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"Download: {self.file_name} by {self.ip_address}"

class AnalyticsSummary(models.Model):
    """Daily analytics summary for performance"""
    date = models.DateField(unique=True)
    total_visits = models.PositiveIntegerField(default=0)
    unique_visitors = models.PositiveIntegerField(default=0)
    total_downloads = models.PositiveIntegerField(default=0)
    unique_downloads = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date']
    
    def __str__(self):
        return f"Analytics for {self.date}: {self.total_visits} visits, {self.total_downloads} downloads"
