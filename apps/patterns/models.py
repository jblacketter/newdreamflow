from django.db import models
from django.conf import settings
from apps.dreams.models import Dream


class DreamPattern(models.Model):
    """AI-identified patterns across multiple dreams."""
    
    PATTERN_TYPES = [
        ('theme', 'Recurring Theme'),
        ('symbol', 'Recurring Symbol'),
        ('entity', 'Recurring Entity'),
        ('emotion', 'Emotional Pattern'),
        ('sequence', 'Sequential Pattern'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='dream_patterns'
    )
    
    pattern_type = models.CharField(
        max_length=20,
        choices=PATTERN_TYPES
    )
    
    name = models.CharField(max_length=100)
    description = models.TextField(
        help_text="AI-generated description of the pattern"
    )
    
    # Pattern data
    confidence_score = models.FloatField(
        default=0.0,
        help_text="AI confidence in this pattern (0-1)"
    )
    
    occurrence_count = models.IntegerField(
        default=0,
        help_text="Number of dreams containing this pattern"
    )
    
    first_occurrence = models.DateField(
        null=True,
        blank=True,
        help_text="Date of first dream with this pattern"
    )
    
    last_occurrence = models.DateField(
        null=True,
        blank=True,
        help_text="Date of most recent dream with this pattern"
    )
    
    # Related dreams
    dreams = models.ManyToManyField(
        Dream,
        related_name='patterns',
        through='DreamPatternOccurrence'
    )
    
    # Visualization data
    visualization_data = models.JSONField(
        default=dict,
        blank=True,
        help_text="Data for pattern visualization"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'dream_patterns'
        ordering = ['-confidence_score', '-occurrence_count']
        unique_together = ['user', 'pattern_type', 'name']
    
    def __str__(self):
        return f"{self.get_pattern_type_display()}: {self.name}"


class DreamPatternOccurrence(models.Model):
    """Tracks specific occurrences of patterns in dreams."""
    
    dream = models.ForeignKey(Dream, on_delete=models.CASCADE)
    pattern = models.ForeignKey(DreamPattern, on_delete=models.CASCADE)
    
    # Context within the dream
    context = models.TextField(
        blank=True,
        help_text="Specific context of pattern in this dream"
    )
    
    strength = models.FloatField(
        default=0.5,
        help_text="Strength of pattern in this dream (0-1)"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'dream_pattern_occurrences'
        unique_together = ['dream', 'pattern']
    
    def __str__(self):
        return f"{self.pattern} in {self.dream}"


class PatternConnection(models.Model):
    """Connections between different patterns."""
    
    pattern1 = models.ForeignKey(
        DreamPattern,
        on_delete=models.CASCADE,
        related_name='connections_from'
    )
    pattern2 = models.ForeignKey(
        DreamPattern,
        on_delete=models.CASCADE,
        related_name='connections_to'
    )
    
    connection_strength = models.FloatField(
        default=0.0,
        help_text="Strength of connection (0-1)"
    )
    
    connection_type = models.CharField(
        max_length=50,
        blank=True,
        help_text="Type of connection"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'pattern_connections'
        unique_together = ['pattern1', 'pattern2']
    
    def __str__(self):
        return f"{self.pattern1} <-> {self.pattern2}"
