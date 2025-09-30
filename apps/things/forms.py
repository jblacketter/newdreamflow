from django import forms
from django.forms import inlineformset_factory
from .models import Thing, ThingTag, ThingImage


class ThingForm(forms.ModelForm):
    tags = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter tags separated by commas',
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-purple-500 focus:border-purple-500'
        })
    )
    
    class Meta:
        model = Thing
        fields = [
            'title', 'description', 'thing_date', 'mood', 
            'lucidity_level', 'privacy_level', 'voice_recording'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-purple-500 focus:border-purple-500',
                'placeholder': 'Give your thing a title (optional)'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-purple-500 focus:border-purple-500',
                'rows': 6,
                'placeholder': 'Describe your thing in detail...'
            }),
            'thing_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-purple-500 focus:border-purple-500'
            }),
            'mood': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-purple-500 focus:border-purple-500',
                'placeholder': 'How did the thing feel? (e.g., peaceful, anxious, exciting)'
            }),
            'lucidity_level': forms.NumberInput(attrs={
                'type': 'range',
                'min': 0,
                'max': 10,
                'class': 'w-full',
                'x-data': '{}',
                'x-model': 'lucidity',
                'x-init': 'lucidity = $el.value'
            }),
            'privacy_level': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-purple-500 focus:border-purple-500'
            }),
            'voice_recording': forms.FileInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-purple-500 focus:border-purple-500',
                'accept': 'audio/*'
            })
        }
    
    def save(self, commit=True):
        thing = super().save(commit=commit)
        
        if commit:
            # Handle tags
            tags_text = self.cleaned_data.get('tags', '')
            if tags_text:
                # Clear existing tags
                thing.tags.clear()
                
                # Add new tags
                tag_names = [tag.strip() for tag in tags_text.split(',') if tag.strip()]
                for tag_name in tag_names:
                    tag, created = ThingTag.objects.get_or_create(
                        name=tag_name.lower(),
                        defaults={'created_by': thing.user}
                    )
                    thing.tags.add(tag)
        
        return thing
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # If editing, populate tags field
        if self.instance.pk:
            self.fields['tags'].initial = ', '.join(
                tag.name for tag in self.instance.tags.all()
            )
        # Remove 'groups' from privacy choices when groups are disabled
        from django.conf import settings
        if not getattr(settings, 'FEATURE_GROUPS', False):
            self.fields['privacy_level'].choices = [
                (val, label) for val, label in self.fields['privacy_level'].choices if val != 'groups'
            ]


class EditThingForm(forms.ModelForm):
    """Form for editing things - excludes voice recording, mood, lucidity level, and tags."""
    
    class Meta:
        model = Thing
        fields = [
            'title', 'description', 'thing_date', 'privacy_level'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-purple-500 focus:border-purple-500',
                'placeholder': 'Give your thing a title (optional)'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-purple-500 focus:border-purple-500',
                'rows': 6,
                'placeholder': 'Describe your thing in detail...'
            }),
            'thing_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-purple-500 focus:border-purple-500'
            }),
            'privacy_level': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-purple-500 focus:border-purple-500'
            })
        }


class ThingImageForm(forms.ModelForm):
    """Form for uploading thing images."""
    
    class Meta:
        model = ThingImage
        fields = ['image', 'image_url']  # Removed caption field
        widgets = {
            'image': forms.FileInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-purple-500 focus:border-purple-500',
                'accept': 'image/*'
            }),
            'image_url': forms.URLInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-purple-500 focus:border-purple-500',
                'placeholder': 'Or paste an image URL'
            })
        }
    
    def clean(self):
        cleaned_data = super().clean()
        image = cleaned_data.get('image')
        image_url = cleaned_data.get('image_url')
        
        # Both empty is OK (the form will be ignored)
        if not image and not image_url:
            return cleaned_data
        
        # Both filled is not OK
        if image and image_url:
            raise forms.ValidationError('Please provide either an image file or an image URL, not both.')
        
        return cleaned_data


# Formset for multiple image uploads
ThingImageFormSet = inlineformset_factory(
    Thing, 
    ThingImage,
    form=ThingImageForm,
    extra=1,  # Just show 1 field by default
    can_delete=True,
    max_num=9  # Maximum 9 images for 3x3 grid
)
