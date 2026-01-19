"""
Script to create admin superuser
Run: python create_admin.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.users.models import User

# Check if admin already exists
phone = '01000000000'
password = 'admin123'

if User.objects.filter(phone_number=phone).exists():
    print(f'Admin with {phone} already exists!')
    user = User.objects.get(phone_number=phone)
    # Reset password
    user.set_password(password)
    user.is_staff = True
    user.is_superuser = True
    user.role = 'admin'
    user.save()
    print('Password has been reset to: admin123')
else:
    admin = User.objects.create_superuser(
        phone_number=phone,
        password=password,
        first_name='Admin'
    )
    print('Superuser created successfully!')

print('\n=== Login Credentials ===')
print(f'Phone: {phone}')
print(f'Password: {password}')
print('=========================')
