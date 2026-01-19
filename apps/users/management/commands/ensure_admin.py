from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import os

class Command(BaseCommand):
    help = 'Creates a default superuser if none exists'

    def handle(self, *args, **options):
        User = get_user_model()
        
        # Default credentials
        PHONE = os.getenv('ADMIN_PHONE', '01000000000')
        PASSWORD = os.getenv('ADMIN_PASSWORD', 'Voltage@2026')
        FIRST_NAME = 'Admin'

        if not User.objects.filter(is_superuser=True).exists():
            self.stdout.write('Creating default superuser...')
            try:
                User.objects.create_superuser(
                    phone_number=PHONE,
                    password=PASSWORD,
                    first_name=FIRST_NAME
                )
                self.stdout.write(self.style.SUCCESS(f'Successfully created superuser: {PHONE} / {PASSWORD}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error creating superuser: {e}'))
        else:
            self.stdout.write('Superuser already exists.')
