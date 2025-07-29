# Dream Journal AI Therapist

## Project Overview
A Django-based dream journal application that uses AI to identify patterns in dreams over time. Features voice recording, pattern visualization, and privacy-focused sharing capabilities.

## Core Design Principles
1. **Privacy First**: 
   - [ ] Dreams are private by default with visual indicators
   - [ ] Encrypted storage for sensitive dream content
   - [ ] Granular sharing controls (private → users → groups → community)

2. **User Experience**:
   - [ ] Quick voice capture for dreams upon waking
   - [ ] Customizable themes and ambient music
   - [ ] Intuitive privacy toggles with clear visual feedback
   - [ ] Personalized "dream face" for shared content

3. **AI Integration**:
   - [ ] Pattern recognition without interpretation bias
   - [ ] Visual mapping of recurring themes/symbols
   - [ ] Connection detection between dreams and life events

## Technical Stack
- **Framework**: Django 5.x
- **Database**: PostgreSQL (production) / SQLite (development)
- **Search**: Algolia (future integration)
- **Frontend**: Django templates + HTMX + Alpine.js
- **AI/ML**: OpenAI API for transcription & pattern analysis
- **Storage**: Local with S3 compatibility for media files
- **Deployment**: PythonAnywhere / Railway

## Project Structure
```
dreamjournal/
├── apps/
│   ├── dreams/        # Core dream models and views
│   ├── patterns/      # AI pattern analysis
│   ├── sharing/       # Privacy and sharing features
│   └── users/         # User profiles and preferences
├── static/            # CSS, JS, themes
├── media/             # User uploads (voice recordings)
├── templates/         # Django templates
└── config/            # Django settings
```

## Development Phases
### Phase 1: Core Foundation *(Current)*
- Django project setup
- Dream model with voice recording
- Basic AI transcription
- Simple CRUD operations

### Phase 2: Privacy & Sharing
- Privacy indicators and controls
- User/group sharing system  
- Custom themes and music
- User "dream faces"

### Phase 3: Production
- Security hardening
- Performance optimization
- Comprehensive testing
- Deployment setup

## Security Considerations
- All dream content encrypted at rest
- API keys in environment variables
- Django security middleware enabled
- HTTPS only in production
- Regular security audits

## Current Focus Areas
- Setting up Django project structure
- Implementing Dream and User models
- Basic voice recording integration

## Communication Template for New Features
When requesting new features, provide:
1. **Goal**: What should this achieve?
2. **Context**: How does it fit with existing code?
3. **Constraints**: Any specific requirements or limitations
4. **Success Criteria**: How do we know it's working correctly?