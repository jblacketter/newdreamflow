@echo off
echo Setting up NewDreamFlow for Windows...
echo.

REM Create virtual environment
echo Creating virtual environment...
python -m venv .venv

REM Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Copy environment file
echo Setting up environment file...
if not exist .env (
    copy .env.example .env
    echo Created .env file from .env.example
    echo Please edit .env to add your configuration
) else (
    echo .env file already exists
)

REM Run migrations
echo Running database migrations...
python manage.py migrate

echo.
echo Setup complete!
echo.
echo To start the development server:
echo   .venv\Scripts\activate
echo   python manage.py runserver
echo.
echo To create a superuser:
echo   .venv\Scripts\activate
echo   python manage.py createsuperuser
echo.
pause