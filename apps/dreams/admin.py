from django.contrib import admin
from .models import Dream, DreamTag, DreamImage


class DreamImageInline(admin.TabularInline):
    model = DreamImage
    extra = 1
    fields = ['image', 'image_url', 'caption', 'order']


@admin.register(Dream)
class DreamAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'dream_date', 'privacy_level', 'lucidity_level', 'created_at']
    list_filter = ['privacy_level', 'dream_date', 'lucidity_level', 'created_at']
    search_fields = ['title', 'description', 'transcription', 'mood']
    readonly_fields = ['id', 'created_at', 'updated_at']
    date_hierarchy = 'dream_date'
    inlines = [DreamImageInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'user', 'title', 'dream_date')
        }),
        ('Content', {
            'fields': ('description', 'voice_recording', 'transcription')
        }),
        ('Metadata', {
            'fields': ('mood', 'lucidity_level', 'privacy_level')
        }),
        ('AI Analysis', {
            'fields': ('themes', 'symbols', 'entities'),
            'classes': ('collapse',)
        }),
        ('Sharing', {
            'fields': ('shared_with_users', 'shared_with_groups'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        })
    )
    
    filter_horizontal = ['shared_with_users', 'shared_with_groups']


@admin.register(DreamTag)
class DreamTagAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_by', 'dream_count', 'created_at']
    search_fields = ['name']
    
    def dream_count(self, obj):
        return obj.dreams.count()
    dream_count.short_description = 'Dreams'


@admin.register(DreamImage)
class DreamImageAdmin(admin.ModelAdmin):
    list_display = ['dream', 'caption', 'order', 'uploaded_at']
    list_filter = ['uploaded_at']
    search_fields = ['caption', 'dream__title']
    ordering = ['dream', 'order']
