# 🌙 NewDreamFlow

A modern web application for recording, analyzing, and sharing dreams with AI-powered insights and pattern recognition.

## Authors
- Dan the man Ray
- Gregory Jon Blacketter

![Python](https://img.shields.io/badge/Python-3.12-blue)
![Django](https://img.shields.io/badge/Django-5.2-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

## ✨ Features

### Core Features
- **Dream Recording**: Write or voice-record your dreams with automatic transcription
- **AI Analysis**: Automatic extraction of themes, symbols, and entities from dreams
- **Pattern Recognition**: Discover recurring patterns across your dream history
- **Privacy Controls**: Choose who can see your dreams (private, specific users, groups, or community)
- **Beautiful Themes**: 7 calming color themes designed for dream journaling

### Social Features
- **Community Feed**: Explore dreams shared by the community with lightning-fast Algolia search
- **Dream Groups**: Create or join groups to share dreams with specific people
- **User Profiles**: Customize your profile with avatars and preferences

### Immersive Experience
- **Background Music**: Ambient sounds to enhance your journaling experience
- **Voice Recording**: Record dreams directly with voice notes
- **Visual Patterns**: Network visualization of dream patterns and connections

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- pip
- virtualenv (recommended)
- PostgreSQL (for production)

### Local Development Setup

#### Quick Setup (Recommended)

**Windows:**
```batch
git clone https://github.com/jblacketter/newdreamflow.git
cd newdreamflow
setup_windows.bat
```

**macOS/Linux:**
```bash
git clone https://github.com/jblacketter/newdreamflow.git
cd newdreamflow
./setup_mac_linux.sh
```

#### Manual Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/jblacketter/newdreamflow.git
   cd newdreamflow
   ```

2. **Create a virtual environment**
   
   **Windows:**
   ```batch
   python -m venv .venv
   .venv\Scripts\activate
   ```
   
   **macOS/Linux:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create a superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the development server**
   ```bash
   python manage.py runserver
   ```

8. **Visit** http://localhost:8000

## 🔧 Configuration

### Required Environment Variables

```env
# Django
SECRET_KEY=your-secret-key-here
DEBUG=True  # Set to False in production

# Database (optional for local dev)
DATABASE_URL=postgresql://user:pass@localhost/dbname

# Algolia Search (optional but recommended)
ALGOLIA_APPLICATION_ID=your-app-id
ALGOLIA_API_KEY=your-admin-key
ALGOLIA_SEARCH_API_KEY=your-search-key

# OpenAI (optional for AI features)
OPENAI_API_KEY=your-openai-key
```

### Optional Features

- **AI Analysis**: Add an OpenAI API key to enable automatic dream analysis
- **Search**: Configure Algolia for lightning-fast community dream search
- **Background Music**: Add MP3 files to `static/music/` for ambient sounds

## 📱 Usage

### Recording Dreams
1. Click "New Dream" in the navigation
2. Choose to write or record your dream
3. Add details like mood, lucidity level, and tags
4. Set privacy level (private, groups, or community)

### Exploring Patterns
1. Visit the "Patterns" page after recording 5+ dreams
2. View AI-detected themes and recurring symbols
3. Explore the interactive network visualization

### Sharing Dreams
1. Create or join groups for sharing with specific people
2. Set dreams to "Community" to share publicly
3. Browse community dreams with search and filters

## 🌐 Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions on deploying to Render.

### Quick Deploy to Render

1. Fork this repository
2. Create a new Web Service on [Render](https://render.com)
3. Connect your GitHub repository
4. Add environment variables in Render dashboard
5. Deploy!

## 🎨 Themes

The app includes 7 beautiful themes:
- **Default Light** - Clean and bright
- **Night Sky** - Dark blue for evening journaling
- **Soft Clouds** - Dreamy pastels
- **Twilight Purple** - Mystical atmosphere
- **Deep Ocean** - Calming blues
- **Forest Green** - Natural and grounding
- **Cosmic Space** - Dark with golden accents

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [Django](https://www.djangoproject.com/)
- Search powered by [Algolia](https://www.algolia.com/)
- AI features powered by [OpenAI](https://openai.com/)
- UI components from [Tailwind CSS](https://tailwindcss.com/)
- Interactive features with [Alpine.js](https://alpinejs.dev/) and [HTMX](https://htmx.org/)

## 📞 Support

For issues and feature requests, please use the [GitHub Issues](https://github.com/jblacketter/newdreamflow/issues) page.

---

Made with 💜 by [jblacketter](https://github.com/jblacketter)