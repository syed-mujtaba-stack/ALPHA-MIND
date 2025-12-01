from django.db import models
from django.contrib.auth.models import User
import uuid
import os

def upload_to(instance, filename):
    """Generate upload path for files"""
    return f'uploads/{instance.user.id}/{uuid.uuid4().hex[:8]}_{filename}'

class FileUpload(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_files')
    file = models.FileField(upload_to=upload_to)
    original_name = models.CharField(max_length=255)
    file_type = models.CharField(max_length=100)
    file_size = models.BigIntegerField(help_text="File size in bytes")
    mime_type = models.CharField(max_length=100)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.original_name}"
    
    @property
    def file_extension(self):
        return os.path.splitext(self.original_name)[1].lower()
    
    @property
    def size_display(self):
        """Human readable file size"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if self.file_size < 1024.0:
                return f"{self.file_size:.1f} {unit}"
            self.file_size /= 1024.0
        return f"{self.file_size:.1f} TB"

class FileAnalysis(models.Model):
    file_upload = models.OneToOneField(FileUpload, on_delete=models.CASCADE, related_name='analysis')
    summary = models.TextField(help_text="AI-generated summary of the file")
    insights = models.JSONField(default=list, help_text="List of key insights")
    metadata = models.JSONField(default=dict, help_text="Extracted metadata")
    analysis_model = models.CharField(max_length=100, help_text="Model used for analysis")
    analysis_time = models.FloatField(help_text="Time taken for analysis in seconds")
    token_count = models.IntegerField(null=True, blank=True)
    cost = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "File Analysis"
        verbose_name_plural = "File Analyses"
    
    def __str__(self):
        return f"Analysis of {self.file_upload.original_name}"

class FileQuery(models.Model):
    file_upload = models.ForeignKey(FileUpload, on_delete=models.CASCADE, related_name='queries')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    query = models.TextField()
    response = models.TextField()
    model = models.CharField(max_length=100)
    tokens_used = models.IntegerField(null=True, blank=True)
    cost = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Query on {self.file_upload.original_name} by {self.user.username}"
