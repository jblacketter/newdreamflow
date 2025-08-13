from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
import uuid


class Dream(models.Model):
    """Core model for storing dreams."""
    
    PRIVACY_CHOICES = [
        ('private', 'Private'),
        ('specific_users', 'Specific Users'),
        ('groups', 'Groups'),
        ('community', 'Community'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='dreams'
    )
    
    # Content
    title = models.CharField(max_length=200, blank=True)
    description = models.TextField(help_text="Dream description")
    voice_recording = models.FileField(
        upload_to='dream_recordings/%Y/%m/',
        null=True,
        blank=True,
        help_text="Voice recording of the dream"
    )
    transcription = models.TextField(
        blank=True,
        help_text="AI transcription of voice recording"
    )
    
    # Privacy settings
    privacy_level = models.CharField(
        max_length=20,
        choices=PRIVACY_CHOICES,
        default='private'
    )
    shared_with_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='shared_dreams',
        blank=True
    )
    shared_with_groups = models.ManyToManyField(
        'sharing.DreamGroup',
        related_name='shared_dreams',
        blank=True
    )
    
    # Metadata
    dream_date = models.DateField(
        default=timezone.now,
        help_text="When the dream occurred"
    )
    mood = models.CharField(
        max_length=50,
        blank=True,
        help_text="Emotional tone of the dream"
    )
    lucidity_level = models.IntegerField(
        default=0,
        help_text="Lucidity level (0-10)"
    )
    
    # AI Analysis
    themes = models.JSONField(
        default=list,
        blank=True,
        help_text="AI-identified themes"
    )
    symbols = models.JSONField(
        default=list,
        blank=True,
        help_text="AI-identified symbols"
    )
    entities = models.JSONField(
        default=list,
        blank=True,
        help_text="People, places, objects in the dream"
    )
    
    # Semantic Analysis
    semantic_verbs = models.JSONField(
        default=list,
        blank=True,
        help_text="Extracted verbs from the description"
    )
    semantic_nouns = models.JSONField(
        default=list,
        blank=True,
        help_text="Extracted nouns from the description"
    )
    semantic_bits = models.JSONField(
        default=dict,
        blank=True,
        help_text="Full semantic analysis including all POS tags"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'dreams'
        ordering = ['-dream_date', '-created_at']
        indexes = [
            models.Index(fields=['-dream_date']),
            models.Index(fields=['user', '-dream_date']),
            models.Index(fields=['privacy_level']),
        ]
    
    def __str__(self):
        return f"{self.title or 'Untitled Dream'} - {self.dream_date}"
    
    def get_absolute_url(self):
        return reverse('dreams:detail', kwargs={'pk': self.pk})
    
    @property
    def is_private(self):
        return self.privacy_level == 'private'
    
    @property
    def is_shared(self):
        return self.privacy_level != 'private'
    
    def is_public_dream(self):
        """Check if dream should be indexed in Algolia (only community dreams)."""
        return self.privacy_level == 'community'
    
    @property
    def string_id(self):
        """Return the ID as a string for Algolia."""
        return str(self.id)


class DreamImage(models.Model):
    """Images associated with dreams."""
    
    dream = models.ForeignKey(
        Dream,
        on_delete=models.CASCADE,
        related_name='images'
    )
    image = models.ImageField(
        upload_to='dream_images/%Y/%m/',
        null=True,
        blank=True,
        help_text="Image file upload"
    )
    image_url = models.URLField(
        max_length=500,
        blank=True,
        help_text="External image URL"
    )
    caption = models.CharField(max_length=200, blank=True)
    order = models.IntegerField(default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'dream_images'
        ordering = ['order', 'uploaded_at']
    
    def __str__(self):
        return f"Image for {self.dream.title or 'Dream'}"
    
    @property
    def get_image_url(self):
        """Return the appropriate image URL."""
        if self.image:
            return self.image.url
        return self.image_url


class DreamTag(models.Model):
    """User-defined tags for dreams."""
    
    name = models.CharField(max_length=50, unique=True)
    dreams = models.ManyToManyField(Dream, related_name='tags')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'dream_tags'
        ordering = ['name']
    
    def __str__(self):
        return self.name
