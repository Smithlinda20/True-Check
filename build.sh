#!/bin/bash
# Build script for Render

set -o errexit

# Install Python dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Apply database migrations
python manage.py migrate

# Create superuser if it doesn't exist
python manage.py shell << END
import os
from core.models import User

email = os.environ.get('ADMIN_EMAIL', 'admin@vericheck.com')
username = os.environ.get('ADMIN_USERNAME', 'admin1')
password = os.environ.get('ADMIN_PASSWORD', 'adim123')

if not User.objects.filter(email=email).exists():
    User.objects.create_superuser(
        email=email,
        username=username,
        password=password
    )
    print(f'✅ Superuser created: {username}')
else:
    print(f'✓ Superuser already exists: {username}')
END

echo "✅ Build complete!"



# Force reset and establish production admin configurations
python fix_admin.py

echo "✅ Build complete!"

