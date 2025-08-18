from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q, Max
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from .models import Thing, ThingTag, ThingImage, Story, StoryThing
from .forms import ThingForm, ThingImageFormSet
from .services.ai_service import ai_service
from .services.semantic_service import semantic_service
from .services.story_service import story_service
import json


def home(request):
    """Homepage view."""
    if request.user.is_authenticated:
        recent_things = Thing.objects.filter(user=request.user).order_by('-thing_date')[:5]
        context = {
            'recent_things': recent_things,
            'total_things': Thing.objects.filter(user=request.user).count(),
        }
    else:
        context = {}
    return render(request, 'things/home.html', context)


@login_required
def quick_capture(request, pk=None):
    """Minimalist quick capture view for frictionless writing - handles both create and edit."""
    thing = None
    if pk:
        thing = get_object_or_404(Thing, pk=pk, user=request.user)
    
    if request.method == 'POST':
        # Handle auto-save via AJAX
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            thing_id = request.POST.get('thing_id')
            content = request.POST.get('content', '')
            
            if thing_id and thing_id != 'new':
                # Update existing thing
                try:
                    thing = Thing.objects.get(pk=thing_id, user=request.user)
                    thing.description = content
                    
                    # Extract title from first line if not set
                    if not thing.title and content:
                        lines = content.split('\n')
                        if lines:
                            # Use first line as title (max 200 chars)
                            thing.title = lines[0][:200].strip('#').strip()
                    
                    # Update semantic analysis in background
                    if content:
                        semantic_analysis = semantic_service.extract_semantic_bits(content)
                        thing.semantic_verbs = semantic_analysis.get('verb_phrases', [])
                        thing.semantic_nouns = semantic_analysis.get('noun_phrases', [])
                        thing.semantic_bits = semantic_analysis
                    
                    thing.save()
                    
                    return JsonResponse({
                        'success': True,
                        'thing_id': str(thing.pk),
                        'word_count': len(content.split()),
                        'saved_at': timezone.now().strftime('%H:%M')
                    })
                except Thing.DoesNotExist:
                    pass
            
            # Create new thing if needed
            if content:  # Only create if there's content
                thing = Thing.objects.create(
                    user=request.user,
                    description=content,
                    title=content.split('\n')[0][:200].strip('#').strip() if content else '',
                    thing_date=timezone.now().date(),
                    privacy_level='private'  # Default to private for minimal friction
                )
                
                # Add semantic analysis
                semantic_analysis = semantic_service.extract_semantic_bits(content)
                thing.semantic_verbs = semantic_analysis.get('verb_phrases', [])
                thing.semantic_nouns = semantic_analysis.get('noun_phrases', [])
                thing.semantic_bits = semantic_analysis
                thing.save()
                
                return JsonResponse({
                    'success': True,
                    'thing_id': str(thing.pk),
                    'word_count': len(content.split()),
                    'saved_at': timezone.now().strftime('%H:%M')
                })
        
        # Handle regular form submission (Cmd+Enter)
        content = request.POST.get('content', '')
        title = request.POST.get('title', '')
        thing_id = request.POST.get('thing_id')
        privacy_level = request.POST.get('privacy_level', 'private')
        thing_date = request.POST.get('thing_date', timezone.now().date())
        
        # Convert date string to date object if needed
        if isinstance(thing_date, str):
            from datetime import datetime
            thing_date = datetime.strptime(thing_date, '%Y-%m-%d').date()
        
        if thing_id and thing_id != 'new':
            thing = get_object_or_404(Thing, pk=thing_id, user=request.user)
            thing.description = content
            thing.title = title
            thing.privacy_level = privacy_level
            thing.thing_date = thing_date
        else:
            thing = Thing(
                user=request.user,
                description=content,
                title=title,
                thing_date=thing_date,
                privacy_level=privacy_level
            )
        
        # Add AI analysis if content exists
        if content:
            analysis = ai_service.analyze_thing(content)
            thing.themes = analysis.get('themes', [])
            thing.symbols = analysis.get('symbols', [])
            thing.entities = analysis.get('entities', [])
            
            # Semantic analysis
            semantic_analysis = semantic_service.extract_semantic_bits(content)
            thing.semantic_verbs = semantic_analysis.get('verb_phrases', [])
            thing.semantic_nouns = semantic_analysis.get('noun_phrases', [])
            thing.semantic_bits = semantic_analysis
        
        thing.save()
        
        # Handle image uploads
        images = request.FILES.getlist('images')
        for image in images:
            ThingImage.objects.create(
                thing=thing,
                image=image
            )
        
        messages.success(request, 'Saved successfully!')
        return redirect('things:detail', pk=thing.pk)
    
    # For GET request, use the thing from pk parameter (already set at the beginning)
    context = {
        'thing': thing,
        'focus_mode': request.GET.get('focus', False)
    }
    return render(request, 'things/quick_capture.html', context)


@login_required
def thing_list(request):
    """List all things for the current user."""
    things = Thing.objects.filter(user=request.user)
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        things = things.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(transcription__icontains=search_query)
        )
    
    # Filter by privacy
    privacy_filter = request.GET.get('privacy', '')
    if privacy_filter:
        things = things.filter(privacy_level=privacy_filter)
    
    # Pagination
    paginator = Paginator(things, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'privacy_filter': privacy_filter,
    }
    return render(request, 'things/thing_list.html', context)


@login_required
def thing_detail(request, pk):
    """Display a single thing."""
    thing = get_object_or_404(Thing, pk=pk)
    
    # Check permissions
    if thing.user != request.user:
        if thing.privacy_level == 'private':
            messages.error(request, "You don't have permission to view this thing.")
            return redirect('things:list')
        elif thing.privacy_level == 'specific_users' and request.user not in thing.shared_with_users.all():
            messages.error(request, "You don't have permission to view this thing.")
            return redirect('things:list')
        elif thing.privacy_level == 'groups':
            user_groups = request.user.thing_groups.all()
            thing_groups = thing.shared_with_groups.all()
            if not any(group in thing_groups for group in user_groups):
                messages.error(request, "You don't have permission to view this thing.")
                return redirect('things:list')
    
    # Generate semantic HTML for the description
    semantic_html = None
    if thing.description:
        semantic_html = semantic_service.create_highlighted_html(thing.description)
    
    # Check if thing can be converted to story
    can_convert_to_story = story_service.is_thing_long_enough(thing)
    
    context = {
        'thing': thing,
        'can_edit': thing.user == request.user,
        'semantic_html': semantic_html,
        'can_convert_to_story': can_convert_to_story,
    }
    return render(request, 'things/thing_detail.html', context)


@login_required
def thing_create(request):
    """Create a new thing."""
    if request.method == 'POST':
        form = ThingForm(request.POST, request.FILES)
        image_formset = ThingImageFormSet(request.POST, request.FILES, prefix='images')
        
        if form.is_valid() and image_formset.is_valid():
            thing = form.save(commit=False)
            thing.user = request.user
            thing.save()
            form.save_m2m()
            
            # Save image formset
            image_formset.instance = thing
            image_formset.save()
            
            # Handle voice transcription if audio file uploaded
            if thing.voice_recording:
                transcription = ai_service.transcribe_audio(thing.voice_recording.path)
                if transcription:
                    thing.transcription = transcription
                    thing.save()
            
            # Analyze thing content
            thing_text = thing.transcription or thing.description
            if thing_text:
                analysis = ai_service.analyze_thing(thing_text)
                thing.themes = analysis.get('themes', [])
                thing.symbols = analysis.get('symbols', [])
                thing.entities = analysis.get('entities', [])
                
                # Semantic bit analysis
                semantic_analysis = semantic_service.extract_semantic_bits(thing_text)
                thing.semantic_verbs = semantic_analysis.get('verb_phrases', [])
                thing.semantic_nouns = semantic_analysis.get('noun_phrases', [])
                thing.semantic_bits = semantic_analysis
                
                thing.save()
            
            messages.success(request, 'Thing recorded successfully!')
            
            # Check if save and continue editing
            if 'save_and_continue' in request.POST:
                return redirect('things:edit', pk=thing.pk)
            else:
                return redirect('things:detail', pk=thing.pk)
    else:
        form = ThingForm(initial={'privacy_level': request.user.default_privacy})
        image_formset = ThingImageFormSet(prefix='images')
    
    return render(request, 'things/thing_form.html', {
        'form': form, 
        'image_formset': image_formset,
        'action': 'Create'
    })


# The thing_edit function has been removed - editing is now handled by quick_capture


@login_required
@require_http_methods(["DELETE"])
def thing_delete(request, pk):
    """Delete a thing."""
    thing = get_object_or_404(Thing, pk=pk, user=request.user)
    thing.delete()
    messages.success(request, 'Thing deleted successfully!')
    return JsonResponse({'success': True})


@login_required
@require_http_methods(["POST"])
def toggle_privacy(request, pk):
    """Toggle thing privacy via HTMX."""
    thing = get_object_or_404(Thing, pk=pk, user=request.user)
    
    # Cycle through privacy levels
    privacy_levels = ['private', 'specific_users', 'groups', 'community']
    current_index = privacy_levels.index(thing.privacy_level)
    new_index = (current_index + 1) % len(privacy_levels)
    thing.privacy_level = privacy_levels[new_index]
    thing.save()
    
    return render(request, 'things/partials/privacy_indicator.html', {'thing': thing})


@login_required
def record_voice(request):
    """Handle voice recording for things."""
    if request.method == 'POST':
        # Handle voice recording upload
        voice_file = request.FILES.get('voice_recording')
        if voice_file:
            # Create thing with voice recording
            thing = Thing.objects.create(
                user=request.user,
                title=request.POST.get('title', ''),
                mood=request.POST.get('mood', ''),
                voice_recording=voice_file,
                thing_date=timezone.now().date(),
                privacy_level=request.user.default_privacy
            )
            
            # Transcribe the audio
            transcription = ai_service.transcribe_audio(thing.voice_recording.path)
            if transcription:
                thing.transcription = transcription
                thing.description = transcription  # Also save as description
                
                # Analyze the thing
                analysis = ai_service.analyze_thing(transcription)
                thing.themes = analysis.get('themes', [])
                thing.symbols = analysis.get('symbols', [])
                thing.entities = analysis.get('entities', [])
            
            thing.save()
            
            # Handle tags
            tags_text = request.POST.get('tags', '')
            if tags_text:
                tag_names = [tag.strip() for tag in tags_text.split(',') if tag.strip()]
                for tag_name in tag_names:
                    tag, created = ThingTag.objects.get_or_create(
                        name=tag_name.lower(),
                        defaults={'created_by': request.user}
                    )
                    thing.tags.add(tag)
            
            messages.success(request, 'Thing recorded and transcribed successfully!')
            return JsonResponse({'success': True, 'redirect_url': f'/things/{thing.pk}/'})
    
    return render(request, 'things/record_voice.html')


def community_things(request):
    """View all things shared with the community."""
    from .services.search_service import algolia_search
    
    # Check if Algolia is enabled
    algolia_config = algolia_search.get_search_settings()
    
    if algolia_config and algolia_config['enabled']:
        # Algolia-powered search
        context = {
            'algolia_config': algolia_config,
            'use_algolia': True,
        }
    else:
        # Fallback to database search
        things = Thing.objects.filter(privacy_level='community').select_related('user').order_by('-created_at')
        
        # Search functionality
        search_query = request.GET.get('search', '')
        if search_query:
            things = things.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(user__username__icontains=search_query)
            )
        
        # Filter by mood
        mood_filter = request.GET.get('mood', '')
        if mood_filter:
            things = things.filter(mood__icontains=mood_filter)
        
        # Pagination
        paginator = Paginator(things, 12)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        # Get unique moods for filter
        all_moods = Thing.objects.filter(
            privacy_level='community'
        ).exclude(mood='').values_list('mood', flat=True).distinct()
        
        context = {
            'page_obj': page_obj,
            'search_query': search_query,
            'mood_filter': mood_filter,
            'all_moods': all_moods,
            'use_algolia': False,
        }
    
    return render(request, 'things/community_things.html', context)


def community_search_api(request):
    """API endpoint for community thing search."""
    from .services.search_service import algolia_search
    
    if not algolia_search.enabled:
        return JsonResponse({'error': 'Search not available'}, status=503)
    
    query = request.GET.get('q', '')
    page = int(request.GET.get('page', 0))
    mood = request.GET.get('mood', '')
    
    filters = []
    if mood:
        filters.append(f'mood:{mood}')
    
    results = algolia_search.search_things(
        query=query,
        filters=' AND '.join(filters) if filters else None,
        page=page,
        per_page=12
    )
    
    return JsonResponse(results)


@login_required
def story_list(request):
    """List all stories for the current user."""
    stories = Story.objects.filter(user=request.user).prefetch_related('things')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        stories = stories.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(stories, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
    }
    return render(request, 'things/story_list.html', context)


@login_required
def story_create(request):
    """Create a new story."""
    if request.method == 'POST':
        title = request.POST.get('title', '')
        description = request.POST.get('description', '')
        privacy_level = request.POST.get('privacy_level', 'private')
        
        if title:
            story = Story.objects.create(
                user=request.user,
                title=title,
                description=description,
                privacy_level=privacy_level
            )
            
            # Add selected things if any
            thing_ids = request.POST.getlist('things')
            for idx, thing_id in enumerate(thing_ids):
                try:
                    thing = Thing.objects.get(pk=thing_id, user=request.user)
                    StoryThing.objects.create(
                        story=story,
                        thing=thing,
                        order=idx
                    )
                except Thing.DoesNotExist:
                    continue
            
            messages.success(request, f'Story "{story.title}" created successfully!')
            return redirect('things:story_edit', pk=story.pk)
    
    # Get user's things for selection
    user_things = Thing.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'user_things': user_things,
    }
    return render(request, 'things/story_create.html', context)


@login_required
def story_detail(request, pk):
    """Display a single story."""
    story = get_object_or_404(Story, pk=pk)
    
    # Check permissions
    if story.user != request.user and story.privacy_level == 'private':
        messages.error(request, "You don't have permission to view this story.")
        return redirect('things:story_list')
    
    # Get ordered things
    story_things = story.story_things.select_related('thing').order_by('order')
    
    context = {
        'story': story,
        'story_things': story_things,
        'can_edit': story.user == request.user,
    }
    return render(request, 'things/story_detail.html', context)


@login_required
def story_edit(request, pk):
    """Edit a story and manage its things."""
    story = get_object_or_404(Story, pk=pk, user=request.user)
    
    if request.method == 'POST':
        # Update story details
        story.title = request.POST.get('title', story.title)
        story.description = request.POST.get('description', story.description)
        story.privacy_level = request.POST.get('privacy_level', story.privacy_level)
        story.save()
        
        # Handle thing ordering
        if 'reorder' in request.POST:
            thing_orders = request.POST.getlist('thing_order')
            for idx, story_thing_id in enumerate(thing_orders):
                try:
                    story_thing = StoryThing.objects.get(pk=story_thing_id, story=story)
                    story_thing.order = idx
                    story_thing.save()
                except StoryThing.DoesNotExist:
                    continue
        
        # Add new things
        if 'add_things' in request.POST:
            thing_ids = request.POST.getlist('new_things')
            max_order = story.story_things.aggregate(Max('order'))['order__max'] or -1
            
            for thing_id in thing_ids:
                try:
                    thing = Thing.objects.get(pk=thing_id, user=request.user)
                    max_order += 1
                    StoryThing.objects.create(
                        story=story,
                        thing=thing,
                        order=max_order
                    )
                except Thing.DoesNotExist:
                    continue
        
        # Remove things
        if 'remove_thing' in request.POST:
            story_thing_id = request.POST.get('remove_thing')
            try:
                story_thing = StoryThing.objects.get(pk=story_thing_id, story=story)
                story_thing.delete()
                
                # Reorder remaining things
                for idx, st in enumerate(story.story_things.order_by('order')):
                    st.order = idx
                    st.save()
            except StoryThing.DoesNotExist:
                pass
        
        messages.success(request, 'Story updated successfully!')
        
        if 'save_and_play' in request.POST:
            return redirect('things:story_play', pk=story.pk)
        else:
            return redirect('things:story_edit', pk=story.pk)
    
    # Get ordered story things
    story_things = story.story_things.select_related('thing').order_by('order')
    
    # Get available things to add (not already in story)
    existing_thing_ids = story.things.values_list('id', flat=True)
    available_things = Thing.objects.filter(user=request.user).exclude(id__in=existing_thing_ids).order_by('-created_at')
    
    context = {
        'story': story,
        'story_things': story_things,
        'available_things': available_things,
    }
    return render(request, 'things/story_edit.html', context)


@login_required
def story_play(request, pk):
    """Play a story - display things in sequence."""
    story = get_object_or_404(Story, pk=pk)
    
    # Check permissions
    if story.user != request.user and story.privacy_level == 'private':
        messages.error(request, "You don't have permission to play this story.")
        return redirect('things:story_list')
    
    # Update play count and last played
    story.played_count += 1
    story.last_played = timezone.now()
    story.save()
    
    # Get ordered things with their timing info
    story_things = story.story_things.select_related('thing').order_by('order')
    
    # Prepare data for the player
    things_data = []
    for st in story_things:
        thing_data = {
            'id': str(st.thing.id),
            'title': st.thing.title or 'Untitled',
            'content': st.thing.description,
            'duration': st.duration * 1000,  # Convert to milliseconds
            'transition': st.transition_type,
            'images': [img.get_image_url for img in st.thing.images.all()]
        }
        things_data.append(thing_data)
    
    context = {
        'story': story,
        'things_data': json.dumps(things_data),
        'total_duration': sum(st.duration for st in story_things),
    }
    return render(request, 'things/story_play.html', context)


@login_required
@require_http_methods(["DELETE"])
def story_delete(request, pk):
    """Delete a story."""
    story = get_object_or_404(Story, pk=pk, user=request.user)
    story.delete()
    messages.success(request, 'Story deleted successfully!')
    return JsonResponse({'success': True})


@login_required
@require_http_methods(["POST"])
def convert_thing_to_story(request, pk):
    """Convert a long Thing into a Story with multiple chunks."""
    thing = get_object_or_404(Thing, pk=pk, user=request.user)
    
    # Check if thing is long enough
    if not story_service.is_thing_long_enough(thing):
        messages.warning(request, 'This thing is too short to convert to a story.')
        return redirect('things:detail', pk=thing.pk)
    
    # Create story from thing
    story_title = request.POST.get('story_title', None)
    story, created_things = story_service.create_story_from_thing(thing, story_title)
    
    if story:
        messages.success(request, f'Successfully created story "{story.title}" with {len(created_things)} parts!')
        return redirect('things:story_detail', pk=story.pk)
    else:
        messages.error(request, 'Could not create story from this thing.')
        return redirect('things:detail', pk=thing.pk)