from django import forms
from django.contrib.auth import get_user_model
from apps.dreams.models import Dream
from .models import DreamGroup

User = get_user_model()


class ShareDreamForm(forms.Form):
    """Form for sharing a dream with users or groups."""
    
    privacy_level = forms.ChoiceField(
        choices=Dream.PRIVACY_CHOICES,
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
        queryset=DreamGroup.objects.none(),
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
        
        self.fields['shared_with_groups'].queryset = DreamGroup.objects.filter(
            members=user
        )