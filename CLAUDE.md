# Thing Journal - Semantic Writing Platform

## Project Overview
A Django-based writing platform built on semantic bit theory concepts that uses AI to identify patterns in written content over time. The platform supports various forms of writing including fiction, journals, and dreams (as a future specialized category). Features voice recording, pattern visualization, and privacy-focused sharing capabilities.

## Core Design Principles
1. **Privacy First**: 
   - [ ] Things are private by default with visual indicators
   - [ ] Encrypted storage for sensitive content
   - [ ] Granular sharing controls (private → users → groups → community)

2. **User Experience**:
   - [ ] Quick voice capture for thoughts and ideas
   - [ ] Customizable themes and ambient music
   - [ ] Intuitive privacy toggles with clear visual feedback
   - [ ] Personalized "thing face" for shared content

3. **AI Integration**:
   - [ ] Pattern recognition without interpretation bias
   - [ ] Visual mapping of recurring themes/symbols
   - [ ] Connection detection between written content
   - [ ] Semantic bit analysis for deep understanding

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
thingjournal/
├── apps/
│   ├── things/        # Core thing models and views
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
- Thing model with voice recording
- Basic AI transcription
- Simple CRUD operations
- Semantic bit analysis integration

### Phase 2: Privacy & Sharing
- Privacy indicators and controls
- User/group sharing system  
- Custom themes and music
- User "thing faces"
- Category system for specialized content types

### Phase 3: Production
- Security hardening
- Performance optimization
- Comprehensive testing
- Deployment setup

## Security Considerations
- All written content encrypted at rest
- API keys in environment variables
- Django security middleware enabled
- HTTPS only in production
- Regular security audits

## Current Focus Areas
- Setting up Django project structure
- Implementing Thing and User models
- Basic voice recording integration
- Semantic bit analysis for text understanding

## Communication Template for New Features
When requesting new features, provide:
1. **Goal**: What should this achieve?
2. **Context**: How does it fit with existing code?
3. **Constraints**: Any specific requirements or limitations
4. **Success Criteria**: How do we know it's working correctly?