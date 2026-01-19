"""
Courses Models for Voltage Platform
نماذج الفصول والمحاضرات
"""
from django.db import models
from django.conf import settings
import re


def get_youtube_duration(url):
    """Fetch video duration from YouTube URL in minutes"""
    try:
        from pytube import YouTube
        
        # Extract video ID and construct proper URL
        video_id = None
        if 'youtube.com/watch' in url:
            match = re.search(r'v=([a-zA-Z0-9_-]+)', url)
            if match:
                video_id = match.group(1)
        elif 'youtu.be/' in url:
            match = re.search(r'youtu\.be/([a-zA-Z0-9_-]+)', url)
            if match:
                video_id = match.group(1)
        elif 'youtube.com/embed/' in url:
            match = re.search(r'embed/([a-zA-Z0-9_-]+)', url)
            if match:
                video_id = match.group(1)
        
        if video_id:
            yt = YouTube(f'https://www.youtube.com/watch?v={video_id}')
            # Duration is in seconds, convert to minutes
            duration_minutes = yt.length // 60
            return max(1, duration_minutes)  # At least 1 minute
    except Exception as e:
        print(f"Error fetching YouTube duration: {e}")
    return 0


class Chapter(models.Model):
    """الفصل الدراسي"""
    
    GRADE_CHOICES = [
        (1, 'الصف الأول الثانوي'),
        (2, 'الصف الثاني الثانوي'),
        (3, 'الصف الثالث الثانوي'),
    ]
    
    title = models.CharField('عنوان الفصل', max_length=200)
    description = models.TextField('وصف الفصل', blank=True)
    grade = models.IntegerField('السنة الدراسية', choices=GRADE_CHOICES)
    order = models.PositiveIntegerField('الترتيب', default=0)
    thumbnail = models.ImageField(
        'صورة الفصل',
        upload_to='chapters/',
        blank=True,
        null=True
    )
    is_active = models.BooleanField('نشط', default=True)
    created_at = models.DateTimeField('تاريخ الإنشاء', auto_now_add=True)
    
    class Meta:
        verbose_name = 'فصل'
        verbose_name_plural = 'الفصول'
        ordering = ['grade', 'order']
    
    def __str__(self):
        return f"{self.get_grade_display()} - {self.title}"
    
    @property
    def lectures_count(self):
        return self.lectures.count()


class Lecture(models.Model):
    """المحاضرة"""
    
    chapter = models.ForeignKey(
        Chapter,
        on_delete=models.CASCADE,
        related_name='lectures',
        verbose_name='الفصل'
    )
    title = models.CharField('عنوان المحاضرة', max_length=200)
    description = models.TextField('وصف المحاضرة', blank=True)
    
    # Video settings
    video_url = models.URLField(
        'رابط الفيديو (Vimeo/YouTube)',
        help_text='ضع رابط الفيديو من Vimeo أو YouTube'
    )
    duration = models.PositiveIntegerField(
        'مدة الفيديو (بالدقائق)',
        default=0
    )
    
    # PDF file
    pdf_file = models.FileField(
        'ملف الملزمة (PDF)',
        upload_to='lectures_pdfs/',
        blank=True,
        null=True
    )
    
    # Thumbnail image
    thumbnail = models.ImageField(
        'صورة المحاضرة',
        upload_to='lectures/',
        blank=True,
        null=True
    )
    
    # Pricing
    price = models.DecimalField(
        'السعر (جنيه)',
        max_digits=6,
        decimal_places=2,
        default=0
    )
    is_free = models.BooleanField('مجانية', default=False)
    
    # Order and status
    order = models.PositiveIntegerField('الترتيب', default=0)
    is_active = models.BooleanField('نشطة', default=True)
    
    # Timestamps
    created_at = models.DateTimeField('تاريخ الإنشاء', auto_now_add=True)
    updated_at = models.DateTimeField('آخر تحديث', auto_now=True)
    
    class Meta:
        verbose_name = 'محاضرة'
        verbose_name_plural = 'المحاضرات'
        ordering = ['chapter', 'order']
    
    def save(self, *args, **kwargs):
        """Auto-fetch duration from YouTube if not set"""
        # Check if this is a new object or video_url changed
        if self.pk:
            try:
                old_instance = Lecture.objects.get(pk=self.pk)
                url_changed = old_instance.video_url != self.video_url
            except Lecture.DoesNotExist:
                url_changed = True
        else:
            url_changed = True
        
        # Fetch duration if it's 0 or URL changed
        if (self.duration == 0 or url_changed) and self.video_url:
            if 'youtube' in self.video_url or 'youtu.be' in self.video_url:
                fetched_duration = get_youtube_duration(self.video_url)
                if fetched_duration > 0:
                    self.duration = fetched_duration
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.chapter.title} - {self.title}"
    
    @property
    def enrolled_count(self):
        return self.enrollments.count()
    
    @property
    def get_embed_url(self):
        """Convert video URL to embeddable format"""
        import re
        url = self.video_url
        
        # YouTube embed parameters to avoid errors
        youtube_params = "?rel=0&modestbranding=1&enablejsapi=1"
        
        # YouTube: convert watch URL to embed URL
        if 'youtube.com/watch' in url:
            # Extract video ID from watch?v=VIDEO_ID
            match = re.search(r'v=([a-zA-Z0-9_-]+)', url)
            if match:
                video_id = match.group(1)
                return f'https://www.youtube.com/embed/{video_id}{youtube_params}'
        
        # YouTube short URLs: youtu.be/VIDEO_ID
        elif 'youtu.be/' in url:
            match = re.search(r'youtu\.be/([a-zA-Z0-9_-]+)', url)
            if match:
                video_id = match.group(1)
                return f'https://www.youtube.com/embed/{video_id}{youtube_params}'
        
        # Already an embed URL - add params if YouTube
        if 'youtube.com/embed' in url and '?' not in url:
            return f'{url}{youtube_params}'
        
        return url


class Enrollment(models.Model):
    """اشتراك الطالب في المحاضرة"""
    
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='enrollments',
        verbose_name='الطالب'
    )
    lecture = models.ForeignKey(
        Lecture,
        on_delete=models.CASCADE,
        related_name='enrollments',
        verbose_name='المحاضرة'
    )
    
    # Progress tracking
    progress = models.PositiveIntegerField(
        'نسبة المشاهدة %',
        default=0
    )
    is_completed = models.BooleanField('مكتملة', default=False)
    
    # Timestamps
    enrolled_at = models.DateTimeField('تاريخ الاشتراك', auto_now_add=True)
    completed_at = models.DateTimeField('تاريخ الإكمال', null=True, blank=True)
    
    class Meta:
        verbose_name = 'اشتراك'
        verbose_name_plural = 'الاشتراكات'
        unique_together = ['student', 'lecture']
        ordering = ['-enrolled_at']
    
    def __str__(self):
        return f"{self.student.first_name} - {self.lecture.title}"
