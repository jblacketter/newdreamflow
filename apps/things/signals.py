from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from .models import Thing
from .services.search_service import algolia_search
import logging

logger = logging.getLogger(__name__)


@receiver(pre_save, sender=Thing)
def track_privacy_change(sender, instance, **kwargs):
    """Track if privacy level is changing."""
    if instance.pk:
        try:
            old_thing = Thing.objects.get(pk=instance.pk)
            instance._privacy_changed = old_thing.privacy_level != instance.privacy_level
            instance._old_privacy = old_thing.privacy_level
        except Thing.DoesNotExist:
            instance._privacy_changed = False
    else:
        instance._privacy_changed = False


@receiver(post_save, sender=Thing)
def update_thing_in_algolia(sender, instance, created, **kwargs):
    """Update thing in Algolia when saved."""
    if not algolia_search.enabled:
        return
    
    try:
        # If thing is community, add/update in Algolia
        if instance.privacy_level == 'community':
            algolia_search.update_thing_index(instance)
            logger.info(f"Thing {str(instance.id)} indexed in Algolia")
        
        # If privacy changed from community to something else, remove from Algolia
        elif hasattr(instance, '_privacy_changed') and instance._privacy_changed:
            if hasattr(instance, '_old_privacy') and instance._old_privacy == 'community':
                algolia_search.remove_thing_from_index(instance)
                logger.info(f"Thing {str(instance.id)} removed from Algolia (no longer community)")
    except Exception as e:
        logger.error(f"Error updating Algolia index for thing {str(instance.id)}: {e}")
        # Don't let Algolia errors prevent saving the thing


@receiver(post_delete, sender=Thing)
def remove_thing_from_algolia(sender, instance, **kwargs):
    """Remove thing from Algolia when deleted."""
    if not algolia_search.enabled:
        return
    
    try:
        if instance.privacy_level == 'community':
            algolia_search.remove_thing_from_index(instance)
            logger.info(f"Thing {str(instance.id)} removed from Algolia (deleted)")
    except Exception as e:
        logger.error(f"Error removing thing {str(instance.id)} from Algolia: {e}")
        # Don't let Algolia errors prevent deleting the thing