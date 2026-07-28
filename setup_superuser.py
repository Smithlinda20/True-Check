import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Truecheck.settings')
django.setup()

from core.models import User

# Create superuser from environment variables or use defaults
email = os.environ.get('ADMIN_EMAIL', 'admin@vericheck.com')
username = os.environ.get('ADMIN_USERNAME', 'admin1')
password = os.environ.get('ADMIN_PASSWORD', 'adim123')

if not User.objects.filter(email=email).exists():
    User.objects.create_superuser(
        email=email,
        username=username,
        password=password
    )
    print('✅ Superuser created successfully!')
    print(f'   Email: {email}')
    print(f'   Username: {username}')
    print('   Note: Store these credentials securely in your environment variables')
else:
    print('⚠️ Superuser already exists!')
    print(f'   Email: {email}')
    print(f'   Username: {username}')
