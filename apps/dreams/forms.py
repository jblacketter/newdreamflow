from django import forms
from .models import Dream, DreamTag


class DreamForm(forms.ModelForm):
    tags = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter tags separated by commas',
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-purple-500 focus:border-purple-500'
        })
    )
    
    class Meta:
        model = Dream
        fields = [
            'title', 'description', 'dream_date', 'mood', 
            'lucidity_level', 'privacy_level', 'voice_recording'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-purple-500 focus:border-purple-500',
                'placeholder': 'Give your dream a title (optional)'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-purple-500 focus:border-purple-500',
                'rows': 6,
                'placeholder': 'Describe your dream in detail...'
            }),
            'dream_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-purple-500 focus:border-purple-500'
            }),
            'mood': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-purple-500 focus:border-purple-500',
                'placeholder': 'How did the dream feel? (e.g., peaceful, anxious, exciting)'
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
        dream = super().save(commit=commit)
        
        if commit:
            # Handle tags
            tags_text = self.cleaned_data.get('tags', '')
            if tags_text:
                # Clear existing tags
                dream.tags.clear()
                
                # Add new tags
                tag_names = [tag.strip() for tag in tags_text.split(',') if tag.strip()]
                for tag_name in tag_names:
                    tag, created = DreamTag.objects.get_or_create(
                        name=tag_name.lower(),
                        defaults={'created_by': dream.user}
                    )
                    dream.tags.add(tag)
        
        return dream
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # If editing, populate tags field
        if self.instance.pk:
            self.fields['tags'].initial = ', '.join(
                tag.name for tag in self.instance.tags.all()
            )