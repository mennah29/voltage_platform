"""
Exams Models for Voltage Platform
نماذج الامتحانات والأسئلة والنتائج
"""
from django.db import models
from django.conf import settings


class Quiz(models.Model):
    """الامتحان/الكويز"""
    
    lecture = models.ForeignKey(
        'courses.Lecture',
        on_delete=models.CASCADE,
        related_name='quizzes',
        verbose_name='المحاضرة'
    )
    title = models.CharField('عنوان الامتحان', max_length=200)
    description = models.TextField('تعليمات الامتحان', blank=True)
    
    time_limit = models.PositiveIntegerField(
        'الوقت المسموح (بالدقائق)',
        default=15
    )
    passing_score = models.PositiveIntegerField(
        'درجة النجاح (%)',
        default=60
    )
    
    # Settings
    shuffle_questions = models.BooleanField('ترتيب عشوائي للأسئلة', default=True)
    show_answers = models.BooleanField('عرض الإجابات بعد الامتحان', default=True)
    max_attempts = models.PositiveIntegerField('عدد المحاولات المسموحة', default=1)
    
    is_active = models.BooleanField('نشط', default=True)
    created_at = models.DateTimeField('تاريخ الإنشاء', auto_now_add=True)
    
    class Meta:
        verbose_name = 'امتحان'
        verbose_name_plural = 'الامتحانات'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.lecture.title} - {self.title}"
    
    @property
    def questions_count(self):
        return self.questions.count()
    
    @property
    def total_points(self):
        return self.questions.aggregate(
            total=models.Sum('points')
        )['total'] or 0


class Question(models.Model):
    """السؤال"""
    
    ANSWER_CHOICES = [
        ('a', 'أ'),
        ('b', 'ب'),
        ('c', 'ج'),
        ('d', 'د'),
    ]
    
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name='questions',
        verbose_name='الامتحان'
    )
    
    text = models.TextField('نص السؤال')
    image = models.ImageField(
        'صورة السؤال',
        upload_to='questions/',
        blank=True,
        null=True,
        help_text='صورة اختيارية للسؤال (معادلات، رسومات...)'
    )
    
    option_a = models.CharField('الخيار أ', max_length=500, blank=True, default='أ')
    option_b = models.CharField('الخيار ب', max_length=500, blank=True, default='ب')
    option_c = models.CharField('الخيار ج', max_length=500, blank=True, default='ج')
    option_d = models.CharField('الخيار د', max_length=500, blank=True, default='د')
    
    correct_answer = models.CharField(
        'الإجابة الصحيحة',
        max_length=1,
        choices=ANSWER_CHOICES
    )
    
    explanation = models.TextField(
        'شرح الإجابة',
        blank=True,
        help_text='يظهر للطالب بعد الامتحان'
    )
    
    points = models.PositiveIntegerField('الدرجة', default=1)
    order = models.PositiveIntegerField('الترتيب', default=0)
    
    class Meta:
        verbose_name = 'سؤال'
        verbose_name_plural = 'الأسئلة'
        ordering = ['quiz', 'order']
    
    def __str__(self):
        return f"س{self.order}: {self.text[:50]}..."
    
    def get_correct_option_text(self):
        return getattr(self, f'option_{self.correct_answer}')


class StudentResult(models.Model):
    """نتيجة الطالب في الامتحان"""
    
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='quiz_results',
        verbose_name='الطالب'
    )
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name='results',
        verbose_name='الامتحان'
    )
    
    score = models.PositiveIntegerField('الدرجة', default=0)
    total_questions = models.PositiveIntegerField('عدد الأسئلة', default=0)
    correct_answers = models.PositiveIntegerField('الإجابات الصحيحة', default=0)
    
    percentage = models.DecimalField(
        'النسبة المئوية',
        max_digits=5,
        decimal_places=2,
        default=0
    )
    passed = models.BooleanField('ناجح', default=False)
    
    # Answers tracking (JSON)
    answers_data = models.JSONField(
        'بيانات الإجابات',
        default=dict,
        blank=True,
        help_text='تخزين إجابات الطالب'
    )
    
    time_taken = models.PositiveIntegerField(
        'الوقت المستغرق (بالثواني)',
        default=0
    )
    
    attempt_number = models.PositiveIntegerField('رقم المحاولة', default=1)
    started_at = models.DateTimeField('بدأ في', auto_now_add=True)
    completed_at = models.DateTimeField('انتهى في', null=True, blank=True)
    
    class Meta:
        verbose_name = 'نتيجة'
        verbose_name_plural = 'النتائج'
        ordering = ['-completed_at']
    
    def __str__(self):
        status = "✅ ناجح" if self.passed else "❌ راسب"
        return f"{self.student.first_name} - {self.quiz.title} ({self.percentage}%) {status}"
    
    def calculate_result(self):
        """حساب النتيجة النهائية"""
        self.percentage = (
            (self.correct_answers / self.total_questions * 100)
            if self.total_questions > 0 else 0
        )
        self.passed = self.percentage >= self.quiz.passing_score
        
        # Update student battery level based on result
        if self.passed:
            self.student.battery_level = min(
                self.student.battery_level + 10,
                100
            )
        else:
            self.student.battery_level = max(
                self.student.battery_level - 5,
                0
            )
        self.student.save()
