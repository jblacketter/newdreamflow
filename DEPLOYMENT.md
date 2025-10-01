# NewDreamFlow Deployment Guide

## Deployment to Render

This guide covers deploying the NewDreamFlow application to Render with PostgreSQL and Algolia search.

## Deployment to PythonAnywhere (Hacker Plan)

These steps assume you are on the $5/month Hacker plan with the default MySQL database and no managed PostgreSQL instance.

### 1. Prep the Repository

1. Push the latest code (including `mysqlclient` in `requirements.txt`) to GitHub or another git host PythonAnywhere can reach.
2. Confirm `DATABASE_URL` is unset locally so you keep using SQLite during development.
3. Double-check that the Python version in `runtime.txt` is supported by both Render and PythonAnywhere. The repo defaults to Python 3.11.9; if your PythonAnywhere plan only offers a different version, update `runtime.txt` and rebuild on Render so both environments stay aligned.

### 2. Clone and Virtualenv on PythonAnywhere

1. Open a Bash console on PythonAnywhere.
2. Clone the repo: `git clone https://github.com/your-account/newdreamflow.git`.
3. Create a virtualenv that matches the Python version you picked above:
   ```bash
   python3.11 -m venv ~/.virtualenvs/newdreamflow
   source ~/.virtualenvs/newdreamflow/bin/activate
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

### 3. Configure the PythonAnywhere Web App

1. In the **Web** tab, create a new Django web app (manual configuration).
2. Set the virtualenv path to `/home/yourusername/.virtualenvs/newdreamflow`.
3. Point the source code path to `/home/yourusername/newdreamflow`.
4. Edit the WSGI file (`/var/www/yourusername_pythonanywhere_com_wsgi.py`):
   ```python
   import os
   import sys

   project_home = '/home/yourusername/newdreamflow'
   if project_home not in sys.path:
       sys.path.insert(0, project_home)

   os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'newdreamflow.settings')

   from django.core.wsgi import get_wsgi_application
   application = get_wsgi_application()
   ```

### 4. Set Environment Variables

In the **Web** tab → **Environment variables**, add the following key/value pairs. Use the credentials from the PythonAnywhere **Databases** tab and keep everything lowercase (PythonAnywhere treats keys as case sensitive):

- `DATABASE_URL`: `mysql://<db_user>:<db_password>@<db_user>.mysql.pythonanywhere-services.com/<db_name>?charset=utf8mb4`
- `SECRET_KEY`: fresh random string (use `python -c 'import secrets; print(secrets.token_urlsafe(50))'`)
- `DEBUG`: `false`
- `ALLOWED_HOSTS`: `yourusername.pythonanywhere.com`
- `FEATURE_ALGOLIA_ONLY`: `true` if you want to force Algolia
- Optional `ALGOLIA_APPLICATION_ID`, `ALGOLIA_API_KEY`, `ALGOLIA_SEARCH_API_KEY`, `OPENAI_API_KEY`

Tip: keep a local `.env.pythonanywhere` text file with the same keys so you can paste values quickly, but never commit it to git.

### 5. Initialize the App

In your Bash console (with the virtualenv activated) run the bootstrap script below. It wraps the standard Django commands and prints progress so you can spot issues quickly.

```bash
./scripts/pythonanywhere_bootstrap.sh
```

The script runs migrations, collects static files, prompts for a superuser, and seeds Algolia if the keys are present.

### 6. Configure Static Files and Reload

1. In the **Web** tab, set a static files mapping: URL `/static/` → `/home/yourusername/newdreamflow/staticfiles`.
2. Click **Reload** on the web app to pick up code and environment changes.

### 7. Verify

Run through this quick smoke test after every deploy:

1. Visit `https://yourusername.pythonanywhere.com` (incognito window recommended).
2. Log in with the superuser from step 5.
3. Create a dream entry and confirm it shows up immediately in the list view.
4. If Algolia is configured, search for the new dream from the community page; fall back to the database view if `FEATURE_ALGOLIA_ONLY` is `false`.
5. Browse a few static assets (CSS, images) and check your browser network tab for 200 responses to `/static/...`.

## Prerequisites

- GitHub account with the repository
- Render account
- Algolia account (optional but recommended)
- OpenAI API key (optional for AI features)

## Step-by-Step Deployment

### 1. Initial Deployment

1. **Fork or Push Repository**
   - Ensure your code is pushed to GitHub
   - Repository should be accessible from your Render account

2. **Create New Web Service on Render**
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select the `newdreamflow` repository

3. **Configure Build Settings**
   - **Name**: newdreamflow (or your preferred name)
   - **Runtime**: Python
   - **Build Command**: `./build.sh`
   - **Start Command**: `gunicorn newdreamflow.wsgi:application`

### 2. Environment Variables

Add these environment variables in Render dashboard:

```
# Required
SECRET_KEY=<click-generate> (Render will generate this)
DEBUG=false
ALLOWED_HOSTS=newdreamflow.onrender.com (or your-app-name.onrender.com)

# Database - DO NOT SET DATABASE_URL
# Render automatically provides DATABASE_URL for PostgreSQL

# Optional - Algolia Search
ALGOLIA_APPLICATION_ID=your-app-id
ALGOLIA_API_KEY=your-admin-key
ALGOLIA_SEARCH_API_KEY=your-search-key

# Optional - OpenAI
OPENAI_API_KEY=your-openai-key
```

**Important**: Do NOT set DATABASE_URL manually. Render automatically provides this for PostgreSQL.

### 3. Deploy and Initialize

1. **Deploy the Application**
   - Click "Create Web Service"
   - Wait for the build to complete

2. **Run Database Migrations**
   - Go to your service dashboard
   - Click "Shell" tab
   - Run:
   ```bash
   python manage.py migrate
   ```

3. **Create Superuser**
   ```bash
   python manage.py createsuperuser
   ```

4. **Initialize Algolia Index** (if configured)
   ```bash
   python manage.py init_algolia_index
   ```

### 4. Verify Deployment

1. Visit your app at `https://your-app-name.onrender.com`
2. Log in with your superuser credentials
3. Test creating a dream entry
4. If using Algolia, test the search functionality

## Troubleshooting

### Database Connection Issues

If you see SQLite errors after deployment:

1. **Check Environment Variables**
   - Ensure DATABASE_URL is NOT set in Render environment variables
   - The app should use Render's automatically provided PostgreSQL URL

2. **Verify Database Configuration**
   - Open Render Shell
   - Run Python shell and check database settings:
   ```python
   python manage.py shell
   >>> from django.conf import settings
   >>> print(settings.DATABASES['default']['ENGINE'])
   # Should show: django.db.backends.postgresql
   ```

3. **Clear and Restart**
   - If still seeing SQLite errors, restart the service
   - Wait for complete redeployment

### Import Errors

If you encounter import errors with Algolia:
- The codebase has been updated to use the newer algoliasearch-django API
- Ensure you're using the latest code from the repository

### Static Files Not Loading

- WhiteNoise is configured to serve static files
- Run `python manage.py collectstatic` (included in build.sh)
- Check that `STATIC_ROOT` is properly configured

### ALLOWED_HOSTS Error

- Update ALLOWED_HOSTS environment variable to include your Render domain
- Format: `your-app-name.onrender.com` or `.onrender.com` for any subdomain

## Local Development vs Production

### Key Differences

1. **Database**
   - Local: SQLite (default) or PostgreSQL
   - Production: PostgreSQL (provided by Render)

2. **Static Files**
   - Local: Django serves static files
   - Production: WhiteNoise serves static files

3. **Debug Mode**
   - Local: DEBUG=True
   - Production: DEBUG=false

4. **Environment Variables**
   - Local: .env file
   - Production: Render dashboard

### Switching Between Environments

To ensure smooth switching:

1. **Local .env file**
   ```env
   # Remove or comment out DATABASE_URL for local SQLite
   # DATABASE_URL=sqlite:///db.sqlite3
   
   # Or use local PostgreSQL
   # DATABASE_URL=postgresql://user:pass@localhost/dreamjournal_dev
   ```

2. **Production Settings**
   - Never commit .env file
   - Always use environment variables in production
   - Keep DEBUG=false in production

## Data Migration

### From SQLite to PostgreSQL

If migrating existing data:

1. **Export from SQLite** (local)
   ```bash
   python manage.py dumpdata --exclude contenttypes --exclude auth.permission > data.json
   ```

2. **Import to PostgreSQL** (Render Shell)
   ```bash
   python manage.py loaddata data.json
   ```

### Backup Strategy

1. **Database Backups**
   - Render provides automatic daily backups (paid plans)
   - Manual backup: `pg_dump $DATABASE_URL > backup.sql`

2. **Media Files**
   - Consider using Cloudinary or AWS S3 for media storage
   - Not included in database backups

## Performance Optimization

1. **Database Queries**
   - Use `select_related()` and `prefetch_related()`
   - Monitor slow queries in production

2. **Caching**
   - Consider adding Redis for caching (Render add-on)
   - Cache expensive computations

3. **Search Performance**
   - Algolia provides fast search
   - Index only necessary fields

## Security Checklist

- [ ] DEBUG=false in production
- [ ] SECRET_KEY is randomly generated
- [ ] ALLOWED_HOSTS is properly configured
- [ ] SSL is enabled (automatic on Render)
- [ ] Sensitive data is not logged
- [ ] API keys are kept secret
- [ ] Regular security updates

## Monitoring

1. **Application Logs**
   - View in Render dashboard
   - Set up log alerts for errors

2. **Performance Monitoring**
   - Monitor response times
   - Track database query performance

3. **Error Tracking**
   - Consider adding Sentry for error tracking
   - Monitor 500 errors

## Maintenance

### Regular Tasks

1. **Update Dependencies**
   ```bash
   pip list --outdated
   pip install --upgrade package-name
   ```

2. **Database Maintenance**
   - Regular backups
   - Monitor database size
   - Optimize queries as needed

3. **Security Updates**
   - Keep Django updated
   - Monitor security advisories

### Scaling

When your app grows:

1. **Upgrade Render Plan**
   - More CPU/RAM for web service
   - Larger database

2. **Add Services**
   - Redis for caching
   - CDN for static files
   - Background job processing

## Support

- **Render Documentation**: https://render.com/docs
- **Django Documentation**: https://docs.djangoproject.com/
- **Project Issues**: https://github.com/jblacketter/alltalk/issues
