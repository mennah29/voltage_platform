"""
Management command to update video durations for existing lectures
"""
from django.core.management.base import BaseCommand
from apps.courses.models import Lecture, get_youtube_duration


class Command(BaseCommand):
    help = 'Update video durations for all lectures with duration=0'

    def handle(self, *args, **options):
        lectures = Lecture.objects.filter(duration=0)
        updated = 0
        
        for lecture in lectures:
            if lecture.video_url and ('youtube' in lecture.video_url or 'youtu.be' in lecture.video_url):
                self.stdout.write(f'Fetching duration for: {lecture.title}...')
                duration = get_youtube_duration(lecture.video_url)
                
                if duration > 0:
                    lecture.duration = duration
                    lecture.save(update_fields=['duration'])
                    self.stdout.write(self.style.SUCCESS(f'  ✓ {duration} minutes'))
                    updated += 1
                else:
                    self.stdout.write(self.style.WARNING('  ✗ Could not fetch duration'))
        
        self.stdout.write(self.style.SUCCESS(f'\nUpdated {updated} lectures!'))
