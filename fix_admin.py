import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Truecheck.settings')
django.setup()

from core.models import User

# Use your new production credentials here
NEW_EMAIL = os.environ.get('ADMIN_EMAIL', 'admin@truecheck.com')
NEW_USER = os.environ.get('ADMIN_USERNAME', 'Truecheck')
NEW_PASS = os.environ.get('ADMIN_PASSWORD', 'Admin@Truecheck')

# Clean out any old conflicting admin accounts safely
User.objects.filter(email=NEW_EMAIL).delete()
User.objects.filter(username=NEW_USER).delete()

# Create a clean, verified staff superuser account
admin_user = User.objects.create_superuser(
    email=NEW_EMAIL,
    username=NEW_USER,
    password=NEW_PASS
)
admin_user.is_staff = True
admin_user.is_superuser = True
admin_user.is_verified = True  # Ensures your custom user validation system allows entry
admin_user.save()

print(f"🎉 Production Admin Created Successfully! Login with: {NEW_EMAIL}")
