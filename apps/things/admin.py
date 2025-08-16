from django.contrib import admin
from .models import Thing, ThingTag, ThingImage


class ThingImageInline(admin.TabularInline):
    model = ThingImage
    extra = 1
    fields = ['image', 'image_url', 'caption', 'order']


@admin.register(Thing)
class ThingAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'thing_date', 'privacy_level', 'lucidity_level', 'created_at']
    list_filter = ['privacy_level', 'thing_date', 'lucidity_level', 'created_at']
    search_fields = ['title', 'description', 'transcription', 'mood']
    readonly_fields = ['id', 'created_at', 'updated_at']
    date_hierarchy = 'thing_date'
    inlines = [ThingImageInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'user', 'title', 'thing_date')
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
        ('Semantic Analysis', {
            'fields': ('semantic_verbs', 'semantic_nouns', 'semantic_bits'),
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


@admin.register(ThingTag)
class ThingTagAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_by', 'thing_count', 'created_at']
    search_fields = ['name']
    
    def thing_count(self, obj):
        return obj.things.count()
    thing_count.short_description = 'Things'


@admin.register(ThingImage)
class ThingImageAdmin(admin.ModelAdmin):
    list_display = ['thing', 'caption', 'order', 'uploaded_at']
    list_filter = ['uploaded_at']
    search_fields = ['caption', 'thing__title']
    ordering = ['thing', 'order']