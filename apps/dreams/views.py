from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from .models import Dream, DreamTag, DreamImage
from .forms import DreamForm, DreamImageFormSet
from .services.ai_service import ai_service
from .services.semantic_service import semantic_service
import json


def home(request):
    """Homepage view."""
    if request.user.is_authenticated:
        recent_dreams = Dream.objects.filter(user=request.user).order_by('-dream_date')[:5]
        context = {
            'recent_dreams': recent_dreams,
            'total_dreams': Dream.objects.filter(user=request.user).count(),
        }
    else:
        context = {}
    return render(request, 'dreams/home.html', context)


@login_required
def quick_capture(request):
    """Minimalist quick capture view for frictionless writing."""
    if request.method == 'POST':
        # Handle auto-save via AJAX
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            dream_id = request.POST.get('dream_id')
            content = request.POST.get('content', '')
            
            if dream_id and dream_id != 'new':
                # Update existing dream
                try:
                    dream = Dream.objects.get(pk=dream_id, user=request.user)
                    dream.description = content
                    
                    # Extract title from first line if not set
                    if not dream.title and content:
                        lines = content.split('\n')
                        if lines:
                            # Use first line as title (max 200 chars)
                            dream.title = lines[0][:200].strip('#').strip()
                    
                    # Update semantic analysis in background
                    if content:
                        semantic_analysis = semantic_service.extract_semantic_bits(content)
                        dream.semantic_verbs = semantic_analysis.get('verbs', [])
                        dream.semantic_nouns = semantic_analysis.get('nouns', [])
                        dream.semantic_bits = semantic_analysis
                    
                    dream.save()
                    
                    return JsonResponse({
                        'success': True,
                        'dream_id': str(dream.pk),
                        'word_count': len(content.split()),
                        'saved_at': timezone.now().strftime('%H:%M')
                    })
                except Dream.DoesNotExist:
                    pass
            
            # Create new dream if needed
            if content:  # Only create if there's content
                dream = Dream.objects.create(
                    user=request.user,
                    description=content,
                    title=content.split('\n')[0][:200].strip('#').strip() if content else '',
                    dream_date=timezone.now().date(),
                    privacy_level='private'  # Default to private for minimal friction
                )
                
                # Add semantic analysis
                semantic_analysis = semantic_service.extract_semantic_bits(content)
                dream.semantic_verbs = semantic_analysis.get('verbs', [])
                dream.semantic_nouns = semantic_analysis.get('nouns', [])
                dream.semantic_bits = semantic_analysis
                dream.save()
                
                return JsonResponse({
                    'success': True,
                    'dream_id': str(dream.pk),
                    'word_count': len(content.split()),
                    'saved_at': timezone.now().strftime('%H:%M')
                })
        
        # Handle regular form submission (Cmd+Enter)
        content = request.POST.get('content', '')
        title = request.POST.get('title', '')
        dream_id = request.POST.get('dream_id')
        
        if dream_id and dream_id != 'new':
            dream = get_object_or_404(Dream, pk=dream_id, user=request.user)
            dream.description = content
            dream.title = title
        else:
            dream = Dream(
                user=request.user,
                description=content,
                title=title,
                dream_date=timezone.now().date(),
                privacy_level='private'  # Always private by default
            )
        
        # Add AI analysis if content exists
        if content:
            analysis = ai_service.analyze_dream(content)
            dream.themes = analysis.get('themes', [])
            dream.symbols = analysis.get('symbols', [])
            dream.entities = analysis.get('entities', [])
            
            # Semantic analysis
            semantic_analysis = semantic_service.extract_semantic_bits(content)
            dream.semantic_verbs = semantic_analysis.get('verbs', [])
            dream.semantic_nouns = semantic_analysis.get('nouns', [])
            dream.semantic_bits = semantic_analysis
        
        dream.save()
        
        # Handle image uploads
        images = request.FILES.getlist('images')
        for image in images:
            DreamImage.objects.create(
                dream=dream,
                image=image
            )
        
        messages.success(request, 'Saved successfully!')
        return redirect('dreams:detail', pk=dream.pk)
    
    # GET request - check if editing existing dream
    dream_id = request.GET.get('edit')
    dream = None
    if dream_id:
        dream = get_object_or_404(Dream, pk=dream_id, user=request.user)
    
    context = {
        'dream': dream,
        'focus_mode': request.GET.get('focus', False)
    }
    return render(request, 'dreams/quick_capture.html', context)


@login_required
def dream_list(request):
    """List all dreams for the current user."""
    dreams = Dream.objects.filter(user=request.user)
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        dreams = dreams.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(transcription__icontains=search_query)
        )
    
    # Filter by privacy
    privacy_filter = request.GET.get('privacy', '')
    if privacy_filter:
        dreams = dreams.filter(privacy_level=privacy_filter)
    
    # Pagination
    paginator = Paginator(dreams, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'privacy_filter': privacy_filter,
    }
    return render(request, 'dreams/dream_list.html', context)


@login_required
def dream_detail(request, pk):
    """Display a single dream."""
    dream = get_object_or_404(Dream, pk=pk)
    
    # Check permissions
    if dream.user != request.user:
        if dream.privacy_level == 'private':
            messages.error(request, "You don't have permission to view this dream.")
            return redirect('dreams:list')
        elif dream.privacy_level == 'specific_users' and request.user not in dream.shared_with_users.all():
            messages.error(request, "You don't have permission to view this dream.")
            return redirect('dreams:list')
        elif dream.privacy_level == 'groups':
            user_groups = request.user.dream_groups.all()
            dream_groups = dream.shared_with_groups.all()
            if not any(group in dream_groups for group in user_groups):
                messages.error(request, "You don't have permission to view this dream.")
                return redirect('dreams:list')
    
    # Generate semantic HTML for the description
    semantic_html = None
    if dream.description:
        semantic_html = semantic_service.create_highlighted_html(dream.description)
    
    context = {
        'dream': dream,
        'can_edit': dream.user == request.user,
        'semantic_html': semantic_html,
    }
    return render(request, 'dreams/dream_detail.html', context)


@login_required
def dream_create(request):
    """Create a new dream."""
    if request.method == 'POST':
        form = DreamForm(request.POST, request.FILES)
        image_formset = DreamImageFormSet(request.POST, request.FILES, prefix='images')
        
        if form.is_valid() and image_formset.is_valid():
            dream = form.save(commit=False)
            dream.user = request.user
            dream.save()
            form.save_m2m()
            
            # Save image formset
            image_formset.instance = dream
            image_formset.save()
            
            # Handle voice transcription if audio file uploaded
            if dream.voice_recording:
                transcription = ai_service.transcribe_audio(dream.voice_recording.path)
                if transcription:
                    dream.transcription = transcription
                    dream.save()
            
            # Analyze dream content
            dream_text = dream.transcription or dream.description
            if dream_text:
                analysis = ai_service.analyze_dream(dream_text)
                dream.themes = analysis.get('themes', [])
                dream.symbols = analysis.get('symbols', [])
                dream.entities = analysis.get('entities', [])
                
                # Semantic bit analysis
                semantic_analysis = semantic_service.extract_semantic_bits(dream_text)
                dream.semantic_verbs = semantic_analysis.get('verbs', [])
                dream.semantic_nouns = semantic_analysis.get('nouns', [])
                dream.semantic_bits = semantic_analysis
                
                dream.save()
            
            messages.success(request, 'Dream recorded successfully!')
            
            # Check if save and continue editing
            if 'save_and_continue' in request.POST:
                return redirect('dreams:edit', pk=dream.pk)
            else:
                return redirect('dreams:detail', pk=dream.pk)
    else:
        form = DreamForm(initial={'privacy_level': request.user.default_privacy})
        image_formset = DreamImageFormSet(prefix='images')
    
    return render(request, 'dreams/dream_form.html', {
        'form': form, 
        'image_formset': image_formset,
        'action': 'Create'
    })


@login_required
def dream_edit(request, pk):
    """Edit an existing dream."""
    dream = get_object_or_404(Dream, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = DreamForm(request.POST, request.FILES, instance=dream)
        image_formset = DreamImageFormSet(request.POST, request.FILES, instance=dream, prefix='images')
        
        if form.is_valid() and image_formset.is_valid():
            dream = form.save()
            image_formset.save()
            
            # Re-analyze if content changed
            if 'description' in form.changed_data or 'voice_recording' in form.changed_data:
                # Handle new voice transcription
                if 'voice_recording' in form.changed_data and dream.voice_recording:
                    transcription = ai_service.transcribe_audio(dream.voice_recording.path)
                    if transcription:
                        dream.transcription = transcription
                
                # Re-analyze dream content
                dream_text = dream.transcription or dream.description
                if dream_text:
                    analysis = ai_service.analyze_dream(dream_text)
                    dream.themes = analysis.get('themes', [])
                    dream.symbols = analysis.get('symbols', [])
                    dream.entities = analysis.get('entities', [])
                    
                    # Semantic bit analysis
                    semantic_analysis = semantic_service.extract_semantic_bits(dream_text)
                    dream.semantic_verbs = semantic_analysis.get('verbs', [])
                    dream.semantic_nouns = semantic_analysis.get('nouns', [])
                    dream.semantic_bits = semantic_analysis
                    
                    dream.save()
            
            messages.success(request, 'Dream updated successfully!')
            
            # Check if save and continue editing
            if 'save_and_continue' in request.POST:
                return redirect('dreams:edit', pk=dream.pk)
            else:
                return redirect('dreams:detail', pk=dream.pk)
    else:
        form = DreamForm(instance=dream)
        image_formset = DreamImageFormSet(instance=dream, prefix='images')
    
    return render(request, 'dreams/dream_form.html', {
        'form': form, 
        'image_formset': image_formset,
        'action': 'Edit', 
        'dream': dream
    })


@login_required
@require_http_methods(["DELETE"])
def dream_delete(request, pk):
    """Delete a dream."""
    dream = get_object_or_404(Dream, pk=pk, user=request.user)
    dream.delete()
    messages.success(request, 'Dream deleted successfully!')
    return JsonResponse({'success': True})


@login_required
@require_http_methods(["POST"])
def toggle_privacy(request, pk):
    """Toggle dream privacy via HTMX."""
    dream = get_object_or_404(Dream, pk=pk, user=request.user)
    
    # Cycle through privacy levels
    privacy_levels = ['private', 'specific_users', 'groups', 'community']
    current_index = privacy_levels.index(dream.privacy_level)
    new_index = (current_index + 1) % len(privacy_levels)
    dream.privacy_level = privacy_levels[new_index]
    dream.save()
    
    return render(request, 'dreams/partials/privacy_indicator.html', {'dream': dream})


@login_required
def record_voice(request):
    """Handle voice recording for dreams."""
    if request.method == 'POST':
        # Handle voice recording upload
        voice_file = request.FILES.get('voice_recording')
        if voice_file:
            # Create dream with voice recording
            dream = Dream.objects.create(
                user=request.user,
                title=request.POST.get('title', ''),
                mood=request.POST.get('mood', ''),
                voice_recording=voice_file,
                dream_date=timezone.now().date(),
                privacy_level=request.user.default_privacy
            )
            
            # Transcribe the audio
            transcription = ai_service.transcribe_audio(dream.voice_recording.path)
            if transcription:
                dream.transcription = transcription
                dream.description = transcription  # Also save as description
                
                # Analyze the dream
                analysis = ai_service.analyze_dream(transcription)
                dream.themes = analysis.get('themes', [])
                dream.symbols = analysis.get('symbols', [])
                dream.entities = analysis.get('entities', [])
            
            dream.save()
            
            # Handle tags
            tags_text = request.POST.get('tags', '')
            if tags_text:
                tag_names = [tag.strip() for tag in tags_text.split(',') if tag.strip()]
                for tag_name in tag_names:
                    tag, created = DreamTag.objects.get_or_create(
                        name=tag_name.lower(),
                        defaults={'created_by': request.user}
                    )
                    dream.tags.add(tag)
            
            messages.success(request, 'Dream recorded and transcribed successfully!')
            return JsonResponse({'success': True, 'redirect_url': f'/dreams/{dream.pk}/'})
    
    return render(request, 'dreams/record_voice.html')


def community_dreams(request):
    """View all dreams shared with the community."""
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
        dreams = Dream.objects.filter(privacy_level='community').select_related('user').order_by('-created_at')
        
        # Search functionality
        search_query = request.GET.get('search', '')
        if search_query:
            dreams = dreams.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(user__username__icontains=search_query)
            )
        
        # Filter by mood
        mood_filter = request.GET.get('mood', '')
        if mood_filter:
            dreams = dreams.filter(mood__icontains=mood_filter)
        
        # Pagination
        paginator = Paginator(dreams, 12)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        # Get unique moods for filter
        all_moods = Dream.objects.filter(
            privacy_level='community'
        ).exclude(mood='').values_list('mood', flat=True).distinct()
        
        context = {
            'page_obj': page_obj,
            'search_query': search_query,
            'mood_filter': mood_filter,
            'all_moods': all_moods,
            'use_algolia': False,
        }
    
    return render(request, 'dreams/community_dreams.html', context)


def community_search_api(request):
    """API endpoint for community dream search."""
    from .services.search_service import algolia_search
    
    if not algolia_search.enabled:
        return JsonResponse({'error': 'Search not available'}, status=503)
    
    query = request.GET.get('q', '')
    page = int(request.GET.get('page', 0))
    mood = request.GET.get('mood', '')
    
    filters = []
    if mood:
        filters.append(f'mood:{mood}')
    
    results = algolia_search.search_dreams(
        query=query,
        filters=' AND '.join(filters) if filters else None,
        page=page,
        per_page=12
    )
    
    return JsonResponse(results)