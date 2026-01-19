from django.contrib import admin
from .models import Chapter, Lecture, Enrollment


class LectureInline(admin.TabularInline):
    """Inline lectures within Chapter admin"""
    model = Lecture
    extra = 1
    fields = ['title', 'video_url', 'pdf_file', 'price', 'is_free', 'order', 'is_active']


@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    """Admin for Chapters"""
    
    list_display = ['title', 'grade', 'lectures_count', 'order', 'is_active']
    list_filter = ['grade', 'is_active']
    search_fields = ['title', 'description']
    ordering = ['grade', 'order']
    inlines = [LectureInline]
    
    fieldsets = (
        ('بيانات الفصل', {
            'fields': ('title', 'description', 'grade', 'thumbnail')
        }),
        ('الإعدادات', {
            'fields': ('order', 'is_active')
        }),
    )


@admin.register(Lecture)
class LectureAdmin(admin.ModelAdmin):
    """Admin for Lectures"""
    
    list_display = [
        'title', 
        'chapter', 
        'duration',
        'price', 
        'is_free',
        'enrolled_count',
        'is_active'
    ]
    list_filter = ['chapter__grade', 'chapter', 'is_free', 'is_active']
    search_fields = ['title', 'description', 'chapter__title']
    ordering = ['chapter', 'order']
    
    fieldsets = (
        ('بيانات المحاضرة', {
            'fields': ('chapter', 'title', 'description', 'order')
        }),
        ('الفيديو', {
            'fields': ('video_url', 'duration')
        }),
        ('المرفقات', {
            'fields': ('pdf_file',)
        }),
        ('التسعير', {
            'fields': ('price', 'is_free')
        }),
        ('الإعدادات', {
            'fields': ('is_active',)
        }),
    )


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    """Admin for Enrollments"""
    
    list_display = [
        'student',
        'lecture',
        'progress',
        'is_completed',
        'enrolled_at'
    ]
    list_filter = [
        'is_completed',
        'lecture__chapter__grade',
        'lecture__chapter',
        'enrolled_at'
    ]
    search_fields = [
        'student__phone_number',
        'student__first_name',
        'lecture__title'
    ]
    readonly_fields = ['enrolled_at', 'completed_at']
    date_hierarchy = 'enrolled_at'
