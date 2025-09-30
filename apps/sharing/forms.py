from django import forms
from django.contrib.auth import get_user_model
from apps.things.models import Thing
from .models import ThingGroup

User = get_user_model()


class ShareThingForm(forms.Form):
    """Form for sharing a thing with users or groups."""
    
    privacy_level = forms.ChoiceField(
        choices=Thing.PRIVACY_CHOICES,
        widget=forms.RadioSelect(attrs={
            'class': 'text-purple-600 focus:ring-purple-500'
        })
    )
    
    shared_with_users = forms.ModelMultipleChoiceField(
        queryset=User.objects.none(),
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'rounded border-gray-300 text-purple-600 focus:ring-purple-500'
        })
    )
    
    shared_with_groups = forms.ModelMultipleChoiceField(
        queryset=ThingGroup.objects.none(),
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'rounded border-gray-300 text-purple-600 focus:ring-purple-500'
        })
    )
    
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set querysets based on user
        self.fields['shared_with_users'].queryset = User.objects.exclude(
            id=user.id
        ).filter(is_active=True)
        
        # Respect groups feature flag
        from django.conf import settings
        if getattr(settings, 'FEATURE_GROUPS', False):
            self.fields['shared_with_groups'].queryset = ThingGroup.objects.filter(
                members=user
            )
        else:
            # Hide/disable groups when feature disabled
            self.fields['shared_with_groups'].queryset = ThingGroup.objects.none()
            self.fields['privacy_level'].choices = [
                (val, label) for val, label in self.fields['privacy_level'].choices if val != 'groups'
            ]
