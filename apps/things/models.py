from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
import uuid


class Thing(models.Model):
    """Core model for storing things (formerly dreams)."""
    
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
        related_name='things'
    )
    
    # Content
    title = models.CharField(max_length=200, blank=True)
    description = models.TextField(help_text="Thing description")
    voice_recording = models.FileField(
        upload_to='thing_recordings/%Y/%m/',
        null=True,
        blank=True,
        help_text="Voice recording of the thing"
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
        related_name='shared_things',
        blank=True
    )
    shared_with_groups = models.ManyToManyField(
        'sharing.ThingGroup',
        related_name='shared_things',
        blank=True
    )
    
    # Metadata
    thing_date = models.DateField(
        default=timezone.now,
        help_text="When the thing occurred"
    )
    mood = models.CharField(
        max_length=50,
        blank=True,
        help_text="Emotional tone of the thing"
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
        help_text="People, places, objects in the thing"
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
        db_table = 'things'
        ordering = ['-thing_date', '-created_at']
        indexes = [
            models.Index(fields=['-thing_date']),
            models.Index(fields=['user', '-thing_date']),
            models.Index(fields=['privacy_level']),
        ]
    
    def __str__(self):
        return f"{self.title or 'Untitled Thing'} - {self.thing_date}"
    
    def get_absolute_url(self):
        return reverse('things:detail', kwargs={'pk': self.pk})
    
    @property
    def is_private(self):
        return self.privacy_level == 'private'
    
    @property
    def is_shared(self):
        return self.privacy_level != 'private'
    
    def is_public_thing(self):
        """Check if thing should be indexed in Algolia (only community things)."""
        return self.privacy_level == 'community'
    
    @property
    def string_id(self):
        """Return the ID as a string for Algolia."""
        return str(self.id)


class ThingImage(models.Model):
    """Images associated with things."""
    
    thing = models.ForeignKey(
        Thing,
        on_delete=models.CASCADE,
        related_name='images'
    )
    image = models.ImageField(
        upload_to='thing_images/%Y/%m/',
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
        db_table = 'thing_images'
        ordering = ['order', 'uploaded_at']
    
    def __str__(self):
        return f"Image for {self.thing.title or 'Thing'}"
    
    @property
    def get_image_url(self):
        """Return the appropriate image URL."""
        if self.image:
            return self.image.url
        return self.image_url


class ThingTag(models.Model):
    """User-defined tags for things."""
    
    name = models.CharField(max_length=50, unique=True)
    things = models.ManyToManyField(Thing, related_name='tags')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'thing_tags'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Story(models.Model):
    """A collection of Things arranged in a playable sequence."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='stories'
    )
    
    # Story details
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, help_text="Story description or synopsis")
    
    # Related things
    things = models.ManyToManyField(
        Thing,
        through='StoryThing',
        related_name='stories',
        blank=True
    )
    
    # Privacy settings (inherited from contained things)
    privacy_level = models.CharField(
        max_length=20,
        choices=Thing.PRIVACY_CHOICES,
        default='private'
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    played_count = models.IntegerField(default=0)
    last_played = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'stories'
        ordering = ['-created_at']
        verbose_name_plural = 'Stories'
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('things:story_detail', kwargs={'pk': self.pk})
    
    @property
    def thing_count(self):
        return self.things.count()
    
    @property
    def total_duration(self):
        """Calculate total playback duration (placeholder for future implementation)."""
        return self.things.count() * 5  # Default 5 seconds per thing


class StoryThing(models.Model):
    """Ordered relationship between Story and Thing."""
    
    story = models.ForeignKey(
        Story,
        on_delete=models.CASCADE,
        related_name='story_things'
    )
    thing = models.ForeignKey(
        Thing,
        on_delete=models.CASCADE,
        related_name='thing_stories'
    )
    
    # Order and timing
    order = models.IntegerField(default=0, help_text="Position in the story sequence")
    duration = models.IntegerField(
        default=5,
        help_text="Display duration in seconds"
    )
    transition_type = models.CharField(
        max_length=20,
        default='fade',
        choices=[
            ('fade', 'Fade'),
            ('slide', 'Slide'),
            ('none', 'None'),
        ]
    )
    
    # Metadata
    added_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, help_text="Notes about this thing in the story")
    
    class Meta:
        db_table = 'story_things'
        ordering = ['order', 'added_at']
        unique_together = [['story', 'order']]
    
    def __str__(self):
        return f"{self.story.title} - {self.order}: {self.thing.title or 'Untitled'}"