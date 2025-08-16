from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.db.models import Q
from apps.things.models import Thing
from .models import ThingGroup, GroupMembership, ShareHistory
from .forms import ShareThingForm

User = get_user_model()


@login_required
def groups(request):
    """List thing sharing groups."""
    if request.method == 'POST':
        # Handle group creation
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        is_private = request.POST.get('is_private') == 'on'
        requires_approval = request.POST.get('requires_approval') == 'on'
        
        if name:  # Ensure name is provided
            # Create the group
            group = ThingGroup.objects.create(
                name=name,
                description=description,
                creator=request.user,
                is_private=is_private,
                requires_approval=requires_approval
            )
            
            # Add creator as admin
            GroupMembership.objects.create(
                user=request.user,
                group=group,
                role='admin'
            )
            
            messages.success(request, f'Group "{name}" created successfully!')
        else:
            messages.error(request, 'Group name is required!')
        
        return redirect('sharing:groups')
    
    user_groups = GroupMembership.objects.filter(user=request.user).select_related('group')
    
    # Get public groups the user is not a member of
    user_group_ids = user_groups.values_list('group_id', flat=True)
    public_groups = ThingGroup.objects.filter(
        is_private=False
    ).exclude(id__in=user_group_ids)
    
    context = {
        'user_groups': user_groups,
        'public_groups': public_groups,
        'pending_invitations': 0,  # TODO: Implement invitations
    }
    return render(request, 'sharing/groups.html', context)


@login_required
def share_thing(request, pk):
    """Share a thing with users or groups."""
    thing = get_object_or_404(Thing, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = ShareThingForm(request.user, request.POST)
        if form.is_valid():
            old_privacy = thing.privacy_level
            
            # Update privacy level
            thing.privacy_level = form.cleaned_data['privacy_level']
            
            # Update shared users and groups
            thing.shared_with_users.set(form.cleaned_data['shared_with_users'])
            thing.shared_with_groups.set(form.cleaned_data['shared_with_groups'])
            thing.save()
            
            # Record sharing history
            history = ShareHistory.objects.create(
                thing=thing,
                action='shared' if old_privacy == 'private' else 'modified',
                old_privacy=old_privacy,
                new_privacy=thing.privacy_level,
                performed_by=request.user
            )
            history.affected_users.set(form.cleaned_data['shared_with_users'])
            history.affected_groups.set(form.cleaned_data['shared_with_groups'])
            
            messages.success(request, 'Thing sharing settings updated!')
            return redirect('things:detail', pk=thing.pk)
    else:
        initial = {
            'privacy_level': thing.privacy_level,
            'shared_with_users': thing.shared_with_users.all(),
            'shared_with_groups': thing.shared_with_groups.all()
        }
        form = ShareThingForm(request.user, initial=initial)
    
    context = {
        'thing': thing,
        'form': form
    }
    return render(request, 'sharing/share_thing.html', context)


@login_required
def invite_to_group(request, pk):
    """Invite users to a group."""
    group = get_object_or_404(ThingGroup, pk=pk)
    
    # Check if user has permission to invite (admin or moderator)
    membership = get_object_or_404(GroupMembership, user=request.user, group=group)
    if membership.role not in ['admin', 'moderator']:
        messages.error(request, 'You do not have permission to invite members to this group.')
        return redirect('sharing:groups')
    
    if request.method == 'POST':
        user_ids = request.POST.getlist('users')
        invited_count = 0
        
        for user_id in user_ids:
            try:
                user_to_invite = User.objects.get(pk=user_id)
                # Check if user is already a member
                if not GroupMembership.objects.filter(user=user_to_invite, group=group).exists():
                    GroupMembership.objects.create(
                        user=user_to_invite,
                        group=group,
                        role='member',
                        invited_by=request.user
                    )
                    invited_count += 1
            except User.DoesNotExist:
                pass
        
        if invited_count > 0:
            messages.success(request, f'Successfully invited {invited_count} user(s) to {group.name}!')
        else:
            messages.info(request, 'No new users were invited.')
        
        return redirect('sharing:groups')
    
    # Get users who are not already members
    current_member_ids = group.members.values_list('id', flat=True)
    available_users = User.objects.exclude(id__in=current_member_ids).filter(is_active=True)
    
    context = {
        'group': group,
        'available_users': available_users,
    }
    return render(request, 'sharing/invite_to_group.html', context)


@login_required
def group_things(request, pk):
    """View things shared with a specific group."""
    group = get_object_or_404(ThingGroup, pk=pk)
    
    # Check if user is a member
    if not GroupMembership.objects.filter(user=request.user, group=group).exists():
        messages.error(request, 'You must be a member of this group to view its things.')
        return redirect('sharing:groups')
    
    # Get things shared with this group
    things = Thing.objects.filter(
        privacy_level='groups',
        shared_with_groups=group
    ).select_related('user').order_by('-thing_date')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        things = things.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(user__username__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(things, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'group': group,
        'page_obj': page_obj,
        'search_query': search_query,
        'member_count': group.members.count(),
        'is_admin': GroupMembership.objects.filter(
            user=request.user, 
            group=group, 
            role='admin'
        ).exists()
    }
    return render(request, 'sharing/group_things.html', context)
