from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Avg, Q
from django.utils import timezone
from datetime import timedelta
from django.http import JsonResponse
from apps.things.models import Thing
from apps.things.services.ai_service import ai_service
from .models import ThingPattern, ThingPatternOccurrence
import json


@login_required
def dashboard(request):
    """Pattern analysis dashboard."""
    user_things = Thing.objects.filter(user=request.user)
    
    # Basic statistics
    total_things = user_things.count()
    patterns_found = ThingPattern.objects.filter(user=request.user).count()
    recurring_themes = ThingPattern.objects.filter(
        user=request.user, 
        pattern_type='theme',
        occurrence_count__gte=2
    ).count()
    avg_lucidity = user_things.aggregate(avg=Avg('lucidity_level'))['avg'] or 0
    
    # Recent patterns
    recent_patterns = ThingPattern.objects.filter(
        user=request.user
    ).order_by('-updated_at')[:5]
    
    # Thing frequency timeline (last 30 days)
    timeline_data = []
    timeline_labels = []
    today = timezone.now().date()
    for i in range(30, -1, -7):
        date = today - timedelta(days=i)
        week_start = date - timedelta(days=date.weekday())
        week_end = week_start + timedelta(days=6)
        count = user_things.filter(
            thing_date__gte=week_start,
            thing_date__lte=week_end
        ).count()
        timeline_data.append(count)
        timeline_labels.append(week_start.strftime('%b %d'))
    
    # Mood distribution
    mood_counts = {}
    for thing in user_things.exclude(mood=''):
        mood = thing.mood.lower() if thing.mood else 'unknown'
        mood_counts[mood] = mood_counts.get(mood, 0) + 1
    
    mood_labels = list(mood_counts.keys())
    mood_data = list(mood_counts.values())
    
    # Common symbols
    symbol_counts = {}
    for thing in user_things:
        if thing.symbols:
            for symbol in thing.symbols:
                symbol_counts[symbol] = symbol_counts.get(symbol, 0) + 1
    
    common_symbols = [
        {'name': symbol, 'count': count}
        for symbol, count in sorted(symbol_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    ]
    
    # Run pattern analysis if we have enough things
    if total_things >= 5 and patterns_found == 0:
        analyze_user_patterns(request.user)
        patterns_found = ThingPattern.objects.filter(user=request.user).count()
    
    # AI insights
    ai_insights = []
    if total_things >= 5:
        ai_insights = [
            f"You've recorded {total_things} things with an average lucidity of {avg_lucidity:.1f}/10.",
            f"Your most common mood in things is '{mood_labels[0] if mood_labels else 'varied'}'.",
            f"We've identified {patterns_found} patterns across your things."
        ]
    
    context = {
        'total_things': total_things,
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
    """Run pattern analysis for a user's things."""
    things = Thing.objects.filter(user=user).order_by('thing_date')
    
    if things.count() < 3:
        return
    
    # Prepare things for analysis
    thing_data = []
    for thing in things:
        thing_data.append({
            'id': str(thing.id),
            'date': thing.thing_date.isoformat(),
            'text': thing.transcription or thing.description,
            'themes': thing.themes,
            'symbols': thing.symbols,
            'entities': thing.entities
        })
    
    # Get AI pattern analysis
    patterns = ai_service.find_patterns(thing_data)
    
    # Create pattern records
    for pattern_data in patterns:
        pattern_type_map = {
            'theme': 'theme',
            'symbol': 'symbol',
            'emotion': 'emotion',
            'sequence': 'sequence'
        }
        
        pattern, created = ThingPattern.objects.get_or_create(
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
        
        # Link things to patterns
        for thing_idx in pattern_data.get('occurrences', []):
            if thing_idx < len(things):
                thing = things[thing_idx]
                ThingPatternOccurrence.objects.get_or_create(
                    thing=thing,
                    pattern=pattern,
                    defaults={'strength': 0.7}
                )


@login_required
def pattern_network(request):
    """Generate network data for pattern visualization."""
    patterns = ThingPattern.objects.filter(user=request.user)
    
    # Build nodes for patterns and things
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
    
    # Add thing nodes and edges
    things_added = set()
    for occurrence in ThingPatternOccurrence.objects.filter(pattern__user=request.user).select_related('thing', 'pattern'):
        thing_id = f'thing_{occurrence.thing.id}'
        
        # Add thing node if not already added
        if thing_id not in things_added:
            nodes.append({
                'id': thing_id,
                'label': occurrence.thing.title or f'Thing {occurrence.thing.thing_date}',
                'type': 'thing',
                'group': 'thing',
                'size': 15
            })
            things_added.add(thing_id)
        
        # Add edge between thing and pattern
        edges.append({
            'from': thing_id,
            'to': f'pattern_{occurrence.pattern.id}',
            'strength': occurrence.strength
        })
    
    # Find connections between patterns through shared things
    pattern_connections = {}
    for thing in Thing.objects.filter(user=request.user):
        thing_patterns = list(thing.pattern_occurrences.values_list('pattern_id', flat=True))
        for i in range(len(thing_patterns)):
            for j in range(i + 1, len(thing_patterns)):
                key = tuple(sorted([thing_patterns[i], thing_patterns[j]]))
                pattern_connections[key] = pattern_connections.get(key, 0) + 1
    
    # Add edges between patterns
    for (p1, p2), count in pattern_connections.items():
        if count >= 2:  # Only show connections with 2+ shared things
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