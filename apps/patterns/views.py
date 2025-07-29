from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Avg, Q
from django.utils import timezone
from datetime import timedelta
from django.http import JsonResponse
from apps.dreams.models import Dream
from apps.dreams.services.ai_service import ai_service
from .models import DreamPattern, DreamPatternOccurrence
import json


@login_required
def dashboard(request):
    """Pattern analysis dashboard."""
    user_dreams = Dream.objects.filter(user=request.user)
    
    # Basic statistics
    total_dreams = user_dreams.count()
    patterns_found = DreamPattern.objects.filter(user=request.user).count()
    recurring_themes = DreamPattern.objects.filter(
        user=request.user, 
        pattern_type='theme',
        occurrence_count__gte=2
    ).count()
    avg_lucidity = user_dreams.aggregate(avg=Avg('lucidity_level'))['avg'] or 0
    
    # Recent patterns
    recent_patterns = DreamPattern.objects.filter(
        user=request.user
    ).order_by('-updated_at')[:5]
    
    # Dream frequency timeline (last 30 days)
    timeline_data = []
    timeline_labels = []
    today = timezone.now().date()
    for i in range(30, -1, -7):
        date = today - timedelta(days=i)
        week_start = date - timedelta(days=date.weekday())
        week_end = week_start + timedelta(days=6)
        count = user_dreams.filter(
            dream_date__gte=week_start,
            dream_date__lte=week_end
        ).count()
        timeline_data.append(count)
        timeline_labels.append(week_start.strftime('%b %d'))
    
    # Mood distribution
    mood_counts = {}
    for dream in user_dreams.exclude(mood=''):
        mood = dream.mood.lower() if dream.mood else 'unknown'
        mood_counts[mood] = mood_counts.get(mood, 0) + 1
    
    mood_labels = list(mood_counts.keys())
    mood_data = list(mood_counts.values())
    
    # Common symbols
    symbol_counts = {}
    for dream in user_dreams:
        if dream.symbols:
            for symbol in dream.symbols:
                symbol_counts[symbol] = symbol_counts.get(symbol, 0) + 1
    
    common_symbols = [
        {'name': symbol, 'count': count}
        for symbol, count in sorted(symbol_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    ]
    
    # Run pattern analysis if we have enough dreams
    if total_dreams >= 5 and patterns_found == 0:
        analyze_user_patterns(request.user)
        patterns_found = DreamPattern.objects.filter(user=request.user).count()
    
    # AI insights
    ai_insights = []
    if total_dreams >= 5:
        ai_insights = [
            f"You've recorded {total_dreams} dreams with an average lucidity of {avg_lucidity:.1f}/10.",
            f"Your most common mood in dreams is '{mood_labels[0] if mood_labels else 'varied'}'.",
            f"We've identified {patterns_found} patterns across your dreams."
        ]
    
    context = {
        'total_dreams': total_dreams,
        'patterns_found': patterns_found,
        'recurring_themes': recurring_themes,
        'avg_lucidity': f"{avg_lucidity:.1f}",
        'recent_patterns': recent_patterns,
        'timeline_labels': json.dumps(timeline_labels),
        'timeline_data': json.dumps(timeline_data),
        'mood_labels': json.dumps(mood_labels),
        'mood_data': json.dumps(mood_data),
        'common_symbols': common_symbols,
        'ai_insights': ai_insights,
    }
    
    return render(request, 'patterns/dashboard.html', context)


def analyze_user_patterns(user):
    """Run pattern analysis for a user's dreams."""
    dreams = Dream.objects.filter(user=user).order_by('dream_date')
    
    if dreams.count() < 3:
        return
    
    # Prepare dreams for analysis
    dream_data = []
    for dream in dreams:
        dream_data.append({
            'id': str(dream.id),
            'date': dream.dream_date.isoformat(),
            'text': dream.transcription or dream.description,
            'themes': dream.themes,
            'symbols': dream.symbols,
            'entities': dream.entities
        })
    
    # Get AI pattern analysis
    patterns = ai_service.find_patterns(dream_data)
    
    # Create pattern records
    for pattern_data in patterns:
        pattern_type_map = {
            'theme': 'theme',
            'symbol': 'symbol',
            'emotion': 'emotion',
            'sequence': 'sequence'
        }
        
        pattern, created = DreamPattern.objects.get_or_create(
            user=user,
            pattern_type=pattern_type_map.get(pattern_data.get('type', 'theme'), 'theme'),
            name=pattern_data.get('name', 'Unknown Pattern'),
            defaults={
                'description': pattern_data.get('description', ''),
                'confidence_score': pattern_data.get('confidence', 0.5) * 100,
                'occurrence_count': len(pattern_data.get('occurrences', []))
            }
        )
        
        if not created:
            pattern.confidence_score = pattern_data.get('confidence', 0.5) * 100
            pattern.occurrence_count = len(pattern_data.get('occurrences', []))
            pattern.save()
        
        # Link dreams to patterns
        for dream_idx in pattern_data.get('occurrences', []):
            if dream_idx < len(dreams):
                dream = dreams[dream_idx]
                DreamPatternOccurrence.objects.get_or_create(
                    dream=dream,
                    pattern=pattern,
                    defaults={'strength': 0.7}
                )


@login_required
def pattern_network(request):
    """Generate network data for pattern visualization."""
    patterns = DreamPattern.objects.filter(user=request.user)
    
    # Build nodes for patterns and dreams
    nodes = []
    edges = []
    
    # Add pattern nodes
    for pattern in patterns:
        nodes.append({
            'id': f'pattern_{pattern.id}',
            'label': pattern.name,
            'type': 'pattern',
            'group': pattern.pattern_type,
            'size': min(pattern.occurrence_count * 10, 50)
        })
    
    # Add dream nodes and edges
    dreams_added = set()
    for occurrence in DreamPatternOccurrence.objects.filter(pattern__user=request.user).select_related('dream', 'pattern'):
        dream_id = f'dream_{occurrence.dream.id}'
        
        # Add dream node if not already added
        if dream_id not in dreams_added:
            nodes.append({
                'id': dream_id,
                'label': occurrence.dream.title or f'Dream {occurrence.dream.dream_date}',
                'type': 'dream',
                'group': 'dream',
                'size': 15
            })
            dreams_added.add(dream_id)
        
        # Add edge between dream and pattern
        edges.append({
            'from': dream_id,
            'to': f'pattern_{occurrence.pattern.id}',
            'strength': occurrence.strength
        })
    
    # Find connections between patterns through shared dreams
    pattern_connections = {}
    for dream in Dream.objects.filter(user=request.user):
        dream_patterns = list(dream.pattern_occurrences.values_list('pattern_id', flat=True))
        for i in range(len(dream_patterns)):
            for j in range(i + 1, len(dream_patterns)):
                key = tuple(sorted([dream_patterns[i], dream_patterns[j]]))
                pattern_connections[key] = pattern_connections.get(key, 0) + 1
    
    # Add edges between patterns
    for (p1, p2), count in pattern_connections.items():
        if count >= 2:  # Only show connections with 2+ shared dreams
            edges.append({
                'from': f'pattern_{p1}',
                'to': f'pattern_{p2}',
                'strength': min(count / 10, 1.0),
                'type': 'pattern_connection'
            })
    
    return JsonResponse({
        'nodes': nodes,
        'edges': edges
    })
