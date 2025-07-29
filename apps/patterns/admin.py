from django.contrib import admin
from .models import DreamPattern, DreamPatternOccurrence, PatternConnection


@admin.register(DreamPattern)
class DreamPatternAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'pattern_type', 'confidence_score', 'occurrence_count', 'created_at']
    list_filter = ['pattern_type', 'confidence_score', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'pattern_type', 'name', 'description')
        }),
        ('Pattern Data', {
            'fields': ('confidence_score', 'occurrence_count', 'first_occurrence', 'last_occurrence')
        }),
        ('Visualization', {
            'fields': ('visualization_data',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        })
    )


@admin.register(DreamPatternOccurrence)
class DreamPatternOccurrenceAdmin(admin.ModelAdmin):
    list_display = ['pattern', 'dream', 'strength', 'created_at']
    list_filter = ['strength', 'created_at']
    search_fields = ['context']
    raw_id_fields = ['dream', 'pattern']


@admin.register(PatternConnection)
class PatternConnectionAdmin(admin.ModelAdmin):
    list_display = ['pattern1', 'pattern2', 'connection_strength', 'connection_type', 'created_at']
    list_filter = ['connection_strength', 'connection_type', 'created_at']
    raw_id_fields = ['pattern1', 'pattern2']
