from django.contrib import admin
from .models import ThingGroup, GroupMembership, ShareHistory


@admin.register(ThingGroup)
class ThingGroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'creator', 'member_count', 'is_private', 'requires_approval', 'created_at']
    list_filter = ['is_private', 'requires_approval', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    
    def member_count(self, obj):
        return obj.members.count()
    member_count.short_description = 'Members'


@admin.register(GroupMembership)
class GroupMembershipAdmin(admin.ModelAdmin):
    list_display = ['user', 'group', 'role', 'joined_at', 'invited_by']
    list_filter = ['role', 'joined_at']
    search_fields = ['user__username', 'group__name']
    raw_id_fields = ['user', 'group', 'invited_by']


@admin.register(ShareHistory)
class ShareHistoryAdmin(admin.ModelAdmin):
    list_display = ['thing', 'action', 'performed_by', 'performed_at']
    list_filter = ['action', 'performed_at']
    readonly_fields = ['performed_at']
    raw_id_fields = ['thing', 'performed_by']
    filter_horizontal = ['affected_users', 'affected_groups']
