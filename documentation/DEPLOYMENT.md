# NewDreamFlow Deployment Guide

## Deployment to PythonAnywhere (Hacker Plan)

This guide covers deploying the NewDreamFlow application to PythonAnywhere with automatic deployment via GitHub Actions.

## Prerequisites

- PythonAnywhere Hacker Plan ($5/month minimum)
- GitHub account with the repository
- PythonAnywhere API token
- Optional: Algolia account for search
- Optional: OpenAI API key for AI features

## Initial Setup

### 1. Clone Repository on PythonAnywhere

1. Open a Bash console on PythonAnywhere
2. Clone the repository:
   ```bash
   git clone https://github.com/jblacketter/newdreamflow.git
   cd newdreamflow
   ```

### 2. Create Virtual Environment

Create a Python 3.13 virtual environment (or use the latest available version):

```bash
python3.13 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Run Migrations

Initialize the database:

```bash
python manage.py migrate
```

You should see output showing all migrations being applied.

### 4. Create Superuser

Create an admin account:

```bash
python manage.py createsuperuser
```

Follow the prompts to set username, email, and password.

### 5. Collect Static Files

```bash
python manage.py collectstatic --noinput
```

This copies all static files to the `staticfiles` directory.

### 6. Configure WSGI File

1. Go to the **Web** tab in PythonAnywhere dashboard
2. Click "Add a new web app"
3. Choose "Manual configuration"
4. Select Python 3.13 (or your chosen version)
5. Edit the WSGI configuration file (e.g., `/var/www/gregblacketter_pythonanywhere_com_wsgi.py`)

Replace ALL contents with:

```python
import os
import sys

# Add your project directory to the sys.path
path = '/home/yourusername/newdreamflow'
if path not in sys.path:
    sys.path.insert(0, path)

# Set environment variables
os.environ['SECRET_KEY'] = 'your-secret-key-here'
os.environ['DEBUG'] = 'True'  # Set to 'False' for production with PostgreSQL
os.environ['ALLOWED_HOSTS'] = 'yourusername.pythonanywhere.com'
os.environ['DATABASE_URL'] = ''  # Leave empty to use SQLite

# Optional: Add API keys if using AI features
# os.environ['OPENAI_API_KEY'] = 'your-openai-key'
# os.environ['ALGOLIA_APPLICATION_ID'] = 'your-algolia-app-id'
# os.environ['ALGOLIA_API_KEY'] = 'your-algolia-api-key'
# os.environ['ALGOLIA_SEARCH_API_KEY'] = 'your-algolia-search-key'

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'newdreamflow.settings')

# Import Django WSGI application
from django.core.wsgi import get_wsgi_application
app = get_wsgi_application()
application = app
```

**Important**: Replace:
- `yourusername` with your PythonAnywhere username
- `your-secret-key-here` with a secure secret key (generate with: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`)

### 7. Configure Web App Settings

1. In the Web tab, set **Virtualenv** path:
   ```
   /home/yourusername/newdreamflow/venv
   ```

2. Add **Static files** mapping:
   - URL: `/static/`
   - Directory: `/home/yourusername/newdreamflow/staticfiles`

3. Click the green **Reload** button

### 8. Verify Deployment

Visit `https://yourusername.pythonanywhere.com` and verify:
- Site loads correctly
- You can log in with your superuser account
- Static files (CSS/images) load properly

## Automatic Deployment with GitHub Actions

### 1. Get PythonAnywhere API Token

1. Go to PythonAnywhere → Account → API token
2. Create or view your API token
3. Copy the token

### 2. Add GitHub Secret

1. Go to your GitHub repository settings
2. Navigate to Settings → Secrets and variables → Actions
3. Click "New repository secret"
4. Name: `PYTHONANYWHERE_API_TOKEN`
5. Value: [paste your API token]
6. Click "Add secret"

### 3. GitHub Actions Workflow

The repository already includes `.github/workflows/deploy.yml` which automatically:
- Pulls latest code from GitHub
- Installs dependencies
- Runs migrations
- Collects static files
- Reloads the web app

This runs automatically whenever code is pushed to the `main` branch.

### 4. Manual Deployment

If you need to deploy manually from PythonAnywhere console:

```bash
cd ~/newdreamflow
source venv/bin/activate
git pull origin main
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
touch /var/www/yourusername_pythonanywhere_com_wsgi.py
```

Then reload the web app from the Web tab.

## Environment Configuration

### Development vs Production

**Development (DEBUG=True)**:
- Uses SQLite database
- Detailed error pages
- No DATABASE_URL required

**Production (DEBUG=False)**:
- Requires DATABASE_URL environment variable
- Uses PostgreSQL or MySQL
- Generic error pages

### Using PostgreSQL/MySQL in Production

For production with a database server:

1. Set up database on PythonAnywhere (Databases tab)
2. Update WSGI file environment variables:
   ```python
   os.environ['DEBUG'] = 'False'
   os.environ['DATABASE_URL'] = 'mysql://user:password@host/database'
   ```
3. Install database driver if needed:
   ```bash
   pip install mysqlclient  # for MySQL
   # or
   pip install psycopg2-binary  # for PostgreSQL
   ```

## Optional Features

### Algolia Search

To enable Algolia search:

1. Add environment variables to WSGI file:
   ```python
   os.environ['ALGOLIA_APPLICATION_ID'] = 'your-app-id'
   os.environ['ALGOLIA_API_KEY'] = 'your-admin-key'
   os.environ['ALGOLIA_SEARCH_API_KEY'] = 'your-search-key'
   os.environ['FEATURE_ALGOLIA_ONLY'] = 'true'  # Optional: force Algolia-only
   ```

2. Initialize the index:
   ```bash
   python manage.py init_algolia_index
   ```

### OpenAI Integration

For AI features (transcription, pattern analysis):

Add to WSGI file:
```python
os.environ['OPENAI_API_KEY'] = 'your-openai-key'
```

### spaCy NLP (Optional)

If using semantic pattern analysis:

```bash
source venv/bin/activate
python -m spacy download en_core_web_sm
```

## Troubleshooting

### Site Shows "Something went wrong"

Check the error log:
1. Web tab → Log files section
2. Click on Error log
3. Look at recent errors (bottom of file)

Common issues:
- Missing environment variables
- Incorrect file paths in WSGI
- Virtual environment not activated
- Database connection errors

### Static Files Not Loading

1. Verify static files mapping in Web tab
2. Ensure `collectstatic` was run
3. Check that path is correct: `/home/yourusername/newdreamflow/staticfiles`

### Database Errors

If seeing "DATABASE_URL required" error:
- Ensure `DEBUG = 'True'` in WSGI file for development
- Or set up proper DATABASE_URL for production

### GitHub Actions Not Deploying

1. Verify API token is set in GitHub secrets
2. Check Actions tab for error messages
3. Ensure token has correct permissions
4. Verify username in workflow file matches PythonAnywhere account

## Collaboration Workflow

### For Team Members

1. Clone repository locally
2. Make changes and test locally
3. Commit and push to GitHub:
   ```bash
   git add .
   git commit -m "Description of changes"
   git push origin main
   ```
4. GitHub Actions automatically deploys to PythonAnywhere

### For Repository Owner

Monitor deployments:
- GitHub → Actions tab shows deployment status
- PythonAnywhere → Web tab shows reload history
- Error log shows any deployment issues

## Security Checklist

- [ ] SECRET_KEY is unique and not committed to repository
- [ ] DEBUG=False in production
- [ ] ALLOWED_HOSTS properly configured
- [ ] API keys stored in environment variables only
- [ ] Database credentials not hardcoded
- [ ] HTTPS enabled (automatic on PythonAnywhere)
- [ ] Regular dependency updates
- [ ] `.env` files in `.gitignore`

## Maintenance

### Update Dependencies

```bash
source venv/bin/activate
pip list --outdated
pip install --upgrade package-name
pip freeze > requirements.txt
```

Commit and push updated requirements.txt.

### Database Backups

For SQLite (development):
```bash
cp db.sqlite3 db.sqlite3.backup
```

For production databases, use PythonAnywhere's backup tools or manual exports.

### Monitoring

1. **Error Logs**: Check regularly in Web tab
2. **Access Logs**: Monitor traffic patterns
3. **Server Logs**: Check console output for warnings

## Support Resources

- **PythonAnywhere Help**: https://help.pythonanywhere.com/
- **Django Documentation**: https://docs.djangoproject.com/
- **Repository Issues**: https://github.com/jblacketter/newdreamflow/issues
- **PythonAnywhere Forums**: https://www.pythonanywhere.com/forums/

## Cost Considerations

**PythonAnywhere Hacker Plan ($5/month)**:
- 1 web app
- MySQL database included
- 512MB storage
- HTTPS included
- GitHub Actions deployment (via API)

For larger deployments, consider upgrading to Web Developer plan or higher.