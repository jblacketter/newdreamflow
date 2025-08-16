from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user model with additional fields for thing journal."""
    
    # Profile customization
    thing_face = models.ImageField(
        upload_to='thing_faces/', 
        null=True, 
        blank=True,
        help_text="Avatar displayed on shared things"
    )
    
    # Theme preferences
    theme = models.CharField(
        max_length=50,
        default='default',
        choices=[
            ('default', 'Default Light'),
            ('night', 'Night Sky'),
            ('clouds', 'Soft Clouds'),
            ('twilight', 'Twilight Purple'),
            ('ocean', 'Deep Ocean'),
            ('forest', 'Forest Green'),
            ('cosmic', 'Cosmic Space'),
        ]
    )
    
    background_music = models.CharField(
        max_length=50,
        default='none',
        choices=[
            ('none', 'No Music'),
            ('ambient_forest', 'Forest Ambience'),
            ('meditation_bells', 'Meditation Bells'),
            ('ocean_waves', 'Ocean Waves'),
            ('rain_sounds', 'Gentle Rain'),
            ('tibetan_bowls', 'Tibetan Bowls'),
            ('white_noise', 'White Noise'),
        ]
    )
    
    music_volume = models.IntegerField(
        default=50,
        help_text="Music volume (0-100)"
    )
    
    # Privacy defaults
    default_privacy = models.CharField(
        max_length=20,
        default='private',
        choices=[
            ('private', 'Private'),
            ('friends', 'Friends Only'),
            ('community', 'Community'),
        ]
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
