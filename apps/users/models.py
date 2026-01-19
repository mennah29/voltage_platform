"""
Custom User Model for Voltage Platform
تسجيل الدخول برقم الهاتف بدلاً من الإيميل
"""
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.core.validators import RegexValidator


class UserManager(BaseUserManager):
    """Custom user manager for phone-based authentication"""
    
    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError('رقم الهاتف مطلوب')
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')
        return self.create_user(phone_number, password, **extra_fields)


class User(AbstractUser):
    """
    Custom User Model for Voltage Platform
    - Primary auth via phone_number instead of email
    - Support for students, teachers, and admins
    """
    
    ROLE_CHOICES = [
        ('student', 'طالب'),
        ('teacher', 'مدرس'),
        ('admin', 'أدمن'),
    ]
    
    GRADE_CHOICES = [
        (1, 'الصف الأول الثانوي'),
        (2, 'الصف الثاني الثانوي'),
        (3, 'الصف الثالث الثانوي'),
    ]
    
    GOVERNORATE_CHOICES = [
        ('cairo', 'القاهرة'),
        ('giza', 'الجيزة'),
        ('alexandria', 'الإسكندرية'),
        ('dakahlia', 'الدقهلية'),
        ('sharqia', 'الشرقية'),
        ('qalyubia', 'القليوبية'),
        ('gharbia', 'الغربية'),
        ('monufia', 'المنوفية'),
        ('beheira', 'البحيرة'),
        ('kafr_el_sheikh', 'كفر الشيخ'),
        ('damietta', 'دمياط'),
        ('port_said', 'بورسعيد'),
        ('ismailia', 'الإسماعيلية'),
        ('suez', 'السويس'),
        ('fayoum', 'الفيوم'),
        ('beni_suef', 'بني سويف'),
        ('minya', 'المنيا'),
        ('asyut', 'أسيوط'),
        ('sohag', 'سوهاج'),
        ('qena', 'قنا'),
        ('aswan', 'أسوان'),
        ('luxor', 'الأقصر'),
        ('red_sea', 'البحر الأحمر'),
        ('new_valley', 'الوادي الجديد'),
        ('matruh', 'مطروح'),
        ('north_sinai', 'شمال سيناء'),
        ('south_sinai', 'جنوب سيناء'),
    ]
    
    # Remove username field, use phone_number instead
    username = None
    
    # Phone validation (Egyptian format)
    phone_regex = RegexValidator(
        regex=r'^01[0125][0-9]{8}$',
        message="رقم الهاتف يجب أن يكون بصيغة مصرية صحيحة (01xxxxxxxxx)"
    )
    
    phone_number = models.CharField(
        'رقم الهاتف',
        max_length=11,
        unique=True,
        validators=[phone_regex]
    )
    
    parent_phone = models.CharField(
        'رقم ولي الأمر',
        max_length=11,
        validators=[phone_regex],
        blank=True,
        null=True
    )
    
    role = models.CharField(
        'الدور',
        max_length=10,
        choices=ROLE_CHOICES,
        default='student'
    )
    
    grade = models.IntegerField(
        'السنة الدراسية',
        choices=GRADE_CHOICES,
        null=True,
        blank=True
    )
    
    governorate = models.CharField(
        'المحافظة',
        max_length=20,
        choices=GOVERNORATE_CHOICES,
        blank=True
    )
    
    profile_pic = models.ImageField(
        'صورة الملف الشخصي',
        upload_to='profile_pics/',
        blank=True,
        null=True
    )
    
    battery_level = models.IntegerField(
        'مستوى الشحن',
        default=0,
        help_text='مستوى تقدم الطالب (0-100)'
    )
    
    created_at = models.DateTimeField('تاريخ التسجيل', auto_now_add=True)
    updated_at = models.DateTimeField('آخر تحديث', auto_now=True)
    
    # Use phone_number for authentication
    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['first_name']
    
    objects = UserManager()
    
    class Meta:
        verbose_name = 'مستخدم'
        verbose_name_plural = 'المستخدمين'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.phone_number})"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.phone_number
    
    @property
    def is_student(self):
        return self.role == 'student'
    
    @property
    def is_teacher(self):
        return self.role == 'teacher'


class ActivationCode(models.Model):
    """
    نظام تفعيل الأكواد للمحاضرات
    """
    code = models.CharField('الكود', max_length=12, unique=True)
    lecture = models.ForeignKey(
        'courses.Lecture',
        on_delete=models.CASCADE,
        verbose_name='المحاضرة'
    )
    used_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='مستخدم بواسطة'
    )
    is_used = models.BooleanField('مستخدم', default=False)
    created_at = models.DateTimeField('تاريخ الإنشاء', auto_now_add=True)
    used_at = models.DateTimeField('تاريخ الاستخدام', null=True, blank=True)
    
    class Meta:
        verbose_name = 'كود تفعيل'
        verbose_name_plural = 'أكواد التفعيل'
    
    def __str__(self):
        return f"{self.code} - {self.lecture.title}"
