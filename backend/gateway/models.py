from django.db import models
from django.contrib.auth.models import User
import uuid

class AIModel(models.Model):
    id = models.CharField(max_length=100, primary_key=True)
    name = models.CharField(max_length=200)
    provider = models.CharField(max_length=50, choices=[
        ('openrouter', 'OpenRouter'),
        ('litellm', 'LiteLLM'),
        ('local', 'Local')
    ])
    description = models.TextField(blank=True)
    context_window = models.IntegerField(default=4096)
    max_tokens = models.IntegerField(default=4096)
    input_price = models.DecimalField(max_digits=10, decimal_places=6, default=0)
    output_price = models.DecimalField(max_digits=10, decimal_places=6, default=0)
    capabilities = models.JSONField(default=list, blank=True)
    is_available = models.BooleanField(default=True)
    is_local = models.BooleanField(default=False)
    requires_gpu = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['provider', 'name']
    
    def __str__(self):
        return f"{self.provider} - {self.name}"

class ModelUsage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='model_usage')
    model = models.ForeignKey(AIModel, on_delete=models.CASCADE, related_name='usage')
    session_id = models.UUIDField(null=True, blank=True)
    input_tokens = models.IntegerField(default=0)
    output_tokens = models.IntegerField(default=0)
    total_cost = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    response_time = models.FloatField(help_text="Response time in seconds")
    success = models.BooleanField(default=True)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['model', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.model.name} - {self.created_at}"

class ModelPreference(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='model_preference')
    preferred_model = models.ForeignKey(AIModel, on_delete=models.SET_NULL, null=True, blank=True)
    fallback_models = models.ManyToManyField(AIModel, related_name='fallback_for', blank=True)
    max_cost_per_day = models.DecimalField(max_digits=10, decimal_places=2, default=10.00)
    auto_fallback_enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Model Preference"
        verbose_name_plural = "Model Preferences"
    
    def __str__(self):
        return f"{self.user.username} Preferences"

class SystemMetrics(models.Model):
    date = models.DateField(unique=True)
    total_requests = models.IntegerField(default=0)
    successful_requests = models.IntegerField(default=0)
    failed_requests = models.IntegerField(default=0)
    total_tokens = models.IntegerField(default=0)
    total_cost = models.DecimalField(max_digits=12, decimal_places=4, default=0)
    avg_response_time = models.FloatField(default=0)
    unique_users = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date']
        verbose_name = "System Metrics"
        verbose_name_plural = "System Metrics"
    
    def __str__(self):
        return f"Metrics for {self.date}"
