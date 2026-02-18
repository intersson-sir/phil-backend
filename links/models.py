"""
Models for the links app.
"""
import uuid
from django.db import models
from django.core.validators import URLValidator
from django.utils import timezone


class NegativeLink(models.Model):
    """
    Model representing a negative link that needs to be tracked and managed.
    
    A negative link is content (post, comment, video, article) on various platforms
    that requires monitoring and potential removal.
    """
    
    PLATFORM_CHOICES = [
        ('facebook', 'Facebook'),
        ('twitter', 'Twitter'),
        ('youtube', 'YouTube'),
        ('reddit', 'Reddit'),
        ('other', 'Other'),
    ]
    
    TYPE_CHOICES = [
        ('post', 'Post'),
        ('comment', 'Comment'),
        ('video', 'Video'),
        ('article', 'Article'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('removed', 'Removed'),
        ('in_work', 'In Work'),
        ('pending', 'Pending'),
        ('cancelled', 'Cancelled'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text='Unique identifier for the negative link'
    )
    
    url = models.TextField(
        validators=[URLValidator()],
        help_text='URL of the negative content'
    )
    
    platform = models.CharField(
        max_length=20,
        choices=PLATFORM_CHOICES,
        help_text='Platform where the content is hosted'
    )
    
    type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        help_text='Type of content'
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text='Current status of the link'
    )
    
    detected_at = models.DateTimeField(
        auto_now_add=True,
        help_text='When the link was first detected'
    )
    
    removed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When the link was removed'
    )
    
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='medium',
        help_text='Priority level for handling this link'
    )
    
    manager = models.ForeignKey(
        'managers.Manager',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='negative_links',
        help_text='Manager assigned to handle this link',
    )
    
    notes = models.TextField(
        null=True,
        blank=True,
        help_text='Additional notes about this link'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text='When this record was created'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text='When this record was last updated'
    )
    
    class Meta:
        ordering = ['-detected_at']
        verbose_name = 'Negative Link'
        verbose_name_plural = 'Negative Links'
        indexes = [
            models.Index(fields=['platform', 'status']),
            models.Index(fields=['status', 'priority']),
            models.Index(fields=['manager']),
            models.Index(fields=['detected_at']),
        ]
    
    def __str__(self):
        return f"{self.platform} - {self.type} ({self.status})"
    
    def save(self, *args, **kwargs):
        """
        Override save to automatically set removed_at when status changes to 'removed'.
        """
        if self.status == 'removed' and not self.removed_at:
            self.removed_at = timezone.now()
        elif self.status != 'removed' and self.removed_at:
            # If status changed from removed to something else, clear removed_at
            self.removed_at = None
        
        super().save(*args, **kwargs)
