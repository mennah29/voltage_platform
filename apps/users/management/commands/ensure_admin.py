from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import os

class Command(BaseCommand):
    help = 'Ensures default superuser exists with known credentials'

    def handle(self, *args, **options):
        User = get_user_model()
        
        # Default credentials
        PHONE = os.getenv('ADMIN_PHONE', '01000000000')
        PASSWORD = os.getenv('ADMIN_PASSWORD', 'Voltage@2026')
        FIRST_NAME = 'Admin'

        # Delete existing superuser with this phone if exists
        existing = User.objects.filter(phone_number=PHONE).first()
        if existing:
            existing.delete()
            self.stdout.write(self.style.WARNING(f'Deleted existing user: {PHONE}'))

        # Create fresh superuser
        try:
            User.objects.create_superuser(
                phone_number=PHONE,
                password=PASSWORD,
                first_name=FIRST_NAME
            )
            self.stdout.write(self.style.SUCCESS(f'✅ Created superuser: {PHONE} / {PASSWORD}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error creating superuser: {e}'))
