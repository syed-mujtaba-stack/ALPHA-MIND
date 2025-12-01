from django.db import models
from django.contrib.auth.models import User
import uuid

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    firebase_uid = models.CharField(max_length=128, unique=True, null=True, blank=True)
    display_name = models.CharField(max_length=100, blank=True)
    photo_url = models.URLField(blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    email_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"
    
    def __str__(self):
        return f"{self.user.username} Profile"

class UserSettings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='settings')
    theme = models.CharField(max_length=20, choices=[
        ('light', 'Light'),
        ('dark', 'Dark'),
        ('system', 'System')
    ], default='system')
    default_model = models.CharField(max_length=100, default='gpt-3.5-turbo')
    language = models.CharField(max_length=10, default='en')
    timezone = models.CharField(max_length=50, default='UTC')
    notifications_enabled = models.BooleanField(default=True)
    auto_save_chats = models.BooleanField(default=True)
    max_chats_per_day = models.IntegerField(default=100)
    preferred_voice = models.CharField(max_length=50, default='alloy')
    voice_speed = models.FloatField(default=1.0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "User Settings"
        verbose_name_plural = "User Settings"
    
    def __str__(self):
        return f"{self.user.username} Settings"

class UserUsage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='usage')
    date = models.DateField()
    messages_sent = models.IntegerField(default=0)
    tokens_used = models.IntegerField(default=0)
    files_uploaded = models.IntegerField(default=0)
    voice_calls = models.IntegerField(default=0)
    cost_incurred = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    
    class Meta:
        unique_together = ['user', 'date']
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.user.username} - {self.date}"
