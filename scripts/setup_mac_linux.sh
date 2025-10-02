#!/bin/bash
echo "Setting up NewDreamFlow for macOS/Linux..."
echo

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv .venv

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Copy environment file
echo "Setting up environment file..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Created .env file from .env.example"
    echo "Please edit .env to add your configuration"
else
    echo ".env file already exists"
fi

# Run migrations
echo "Running database migrations..."
python manage.py migrate

echo
echo "Setup complete!"
echo
echo "To start the development server:"
echo "  source .venv/bin/activate"
echo "  python manage.py runserver"
echo
echo "To create a superuser:"
echo "  source .venv/bin/activate"
echo "  python manage.py createsuperuser"
echo