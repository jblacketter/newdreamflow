from django.db import models
from django.conf import settings


class ThingGroup(models.Model):
    """Groups for sharing things."""
    
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    # Members
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_groups'
    )
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='thing_groups',
        through='GroupMembership',
        through_fields=('group', 'user')
    )
    
    # Group settings
    is_private = models.BooleanField(
        default=True,
        help_text="Private groups require invitation"
    )
    requires_approval = models.BooleanField(
        default=False,
        help_text="New members need approval"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'thing_groups'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class GroupMembership(models.Model):
    """Membership in thing sharing groups."""
    
    ROLE_CHOICES = [
        ('member', 'Member'),
        ('moderator', 'Moderator'),
        ('admin', 'Admin'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    group = models.ForeignKey(
        ThingGroup,
        on_delete=models.CASCADE
    )
    
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='member'
    )
    
    joined_at = models.DateTimeField(auto_now_add=True)
    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='group_invitations'
    )
    
    class Meta:
        db_table = 'group_memberships'
        unique_together = ['user', 'group']
    
    def __str__(self):
        return f"{self.user} in {self.group}"


class ShareHistory(models.Model):
    """Track sharing history for things."""
    
    ACTION_CHOICES = [
        ('shared', 'Shared'),
        ('unshared', 'Unshared'),
        ('modified', 'Modified Sharing'),
    ]
    
    thing = models.ForeignKey(
        'things.Thing',
        on_delete=models.CASCADE,
        related_name='share_history'
    )
    
    action = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES
    )
    
    # What changed
    old_privacy = models.CharField(max_length=20, blank=True)
    new_privacy = models.CharField(max_length=20, blank=True)
    
    # Who it was shared with/unshared from
    affected_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='share_notifications'
    )
    affected_groups = models.ManyToManyField(
        ThingGroup,
        blank=True,
        related_name='share_notifications'
    )
    
    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    performed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'share_history'
        ordering = ['-performed_at']
    
    def __str__(self):
        return f"{self.action} {self.thing} at {self.performed_at}"
