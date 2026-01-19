from django.contrib import admin
from .models import Quiz, Question, StudentResult


class QuestionInline(admin.StackedInline):
    """Inline questions within Quiz admin"""
    model = Question
    extra = 1
    
    fieldsets = (
        ('السؤال', {
            'fields': ('order', 'text', 'image'),
            'description': 'أضف نص السؤال والصورة (اختيارية)'
        }),
        ('الاختيارات (أ، ب، ج، د)', {
            'fields': (('option_a', 'option_b'), ('option_c', 'option_d')),
            'classes': ('collapse-open',)
        }),
        ('الإجابة الصحيحة', {
            'fields': ('correct_answer', 'points', 'explanation'),
        }),
    )


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    """Admin for Quizzes"""
    
    list_display = [
        'title',
        'lecture',
        'questions_count',
        'time_limit',
        'passing_score',
        'is_active'
    ]
    list_filter = [
        'lecture__chapter__grade',
        'lecture__chapter',
        'is_active'
    ]
    search_fields = ['title', 'lecture__title']
    inlines = [QuestionInline]
    
    fieldsets = (
        ('بيانات الامتحان', {
            'fields': ('lecture', 'title', 'description')
        }),
        ('إعدادات الامتحان', {
            'fields': (
                'time_limit',
                'passing_score',
                'max_attempts',
                'shuffle_questions',
                'show_answers'
            )
        }),
        ('الحالة', {
            'fields': ('is_active',)
        }),
    )


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    """Admin for Questions (standalone view)"""
    
    list_display = ['order', 'text_preview', 'quiz', 'has_image', 'correct_answer', 'points']
    list_filter = ['quiz__lecture__chapter__grade', 'quiz']
    search_fields = ['text', 'quiz__title']
    
    fieldsets = (
        ('السؤال', {
            'fields': ('quiz', 'order', 'text', 'image'),
        }),
        ('الاختيارات (أ، ب، ج، د)', {
            'fields': (('option_a', 'option_b'), ('option_c', 'option_d')),
        }),
        ('الإجابة الصحيحة', {
            'fields': ('correct_answer', 'points', 'explanation'),
        }),
    )
    
    def text_preview(self, obj):
        return obj.text[:80] + "..." if len(obj.text) > 80 else obj.text
    text_preview.short_description = 'السؤال'
    
    def has_image(self, obj):
        return "✅ صورة" if obj.image else "❌ بدون"
    has_image.short_description = 'صورة'


@admin.register(StudentResult)
class StudentResultAdmin(admin.ModelAdmin):
    """Admin for Student Results with pass/fail tracking"""
    
    list_display = [
        'student',
        'quiz',
        'correct_answers',
        'total_questions',
        'percentage',
        'passed',
        'time_display',
        'completed_at'
    ]
    
    list_filter = [
        'passed',
        'quiz__lecture__chapter__grade',
        'quiz__lecture__chapter',
        'quiz',
        'completed_at'
    ]
    
    search_fields = [
        'student__phone_number',
        'student__first_name',
        'student__last_name',
        'quiz__title'
    ]
    
    readonly_fields = [
        'score',
        'correct_answers',
        'total_questions',
        'percentage',
        'passed',
        'time_taken',
        'answers_data',
        'started_at',
        'completed_at'
    ]
    
    date_hierarchy = 'completed_at'
    
    def time_display(self, obj):
        minutes = obj.time_taken // 60
        seconds = obj.time_taken % 60
        return f"{minutes}:{seconds:02d}"
    time_display.short_description = 'الوقت'
    
    # Actions for bulk operations
    actions = ['export_results']
    
    def export_results(self, request, queryset):
        """Export results to CSV"""
        # This can be expanded to export to Excel
        pass
    export_results.short_description = "تصدير النتائج المحددة"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'student', 'quiz', 'quiz__lecture'
        )
