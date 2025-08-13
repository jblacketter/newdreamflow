from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from .models import Dream
from .services.search_service import algolia_search
import logging

logger = logging.getLogger(__name__)


@receiver(pre_save, sender=Dream)
def track_privacy_change(sender, instance, **kwargs):
    """Track if privacy level is changing."""
    if instance.pk:
        try:
            old_dream = Dream.objects.get(pk=instance.pk)
            instance._privacy_changed = old_dream.privacy_level != instance.privacy_level
            instance._old_privacy = old_dream.privacy_level
        except Dream.DoesNotExist:
            instance._privacy_changed = False
    else:
        instance._privacy_changed = False


@receiver(post_save, sender=Dream)
def update_dream_in_algolia(sender, instance, created, **kwargs):
    """Update dream in Algolia when saved."""
    if not algolia_search.enabled:
        return
    
    try:
        # If dream is community, add/update in Algolia
        if instance.privacy_level == 'community':
            algolia_search.update_dream_index(instance)
            logger.info(f"Dream {str(instance.id)} indexed in Algolia")
        
        # If privacy changed from community to something else, remove from Algolia
        elif hasattr(instance, '_privacy_changed') and instance._privacy_changed:
            if hasattr(instance, '_old_privacy') and instance._old_privacy == 'community':
                algolia_search.remove_dream_from_index(instance)
                logger.info(f"Dream {str(instance.id)} removed from Algolia (no longer community)")
    except Exception as e:
        logger.error(f"Error updating Algolia index for dream {str(instance.id)}: {e}")
        # Don't let Algolia errors prevent saving the dream


@receiver(post_delete, sender=Dream)
def remove_dream_from_algolia(sender, instance, **kwargs):
    """Remove dream from Algolia when deleted."""
    if not algolia_search.enabled:
        return
    
    try:
        if instance.privacy_level == 'community':
            algolia_search.remove_dream_from_index(instance)
            logger.info(f"Dream {str(instance.id)} removed from Algolia (deleted)")
    except Exception as e:
        logger.error(f"Error removing dream {str(instance.id)} from Algolia: {e}")
        # Don't let Algolia errors prevent deleting the dream