#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Apply any outstanding database migrations
python manage.py migrate

# Create superuser if doesn't exist (optional - you might want to do this manually)
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@example.com', 'changeme123')" | python manage.py shell || true

# Collect static files
python manage.py collectstatic --no-input
