"""
Payment Models for Voltage Platform
نماذج الدفع - فوري ومحفظة اتصالات
"""
from django.db import models
from django.conf import settings
import random
import string


class WalletConfig(models.Model):
    """إعدادات المحفظة - تُدار من الـ Admin"""
    
    WALLET_TYPE_CHOICES = [
        ('etisalat', 'اتصالات كاش'),
        ('vodafone', 'فودافون كاش'),
        ('orange', 'أورانج كاش'),
        ('we', 'وي باي'),
    ]
    
    wallet_type = models.CharField(
        'نوع المحفظة',
        max_length=20,
        choices=WALLET_TYPE_CHOICES,
        default='etisalat'
    )
    wallet_number = models.CharField(
        'رقم المحفظة',
        max_length=15,
        help_text='رقم الموبايل المسجل عليه المحفظة'
    )
    wallet_name = models.CharField(
        'اسم صاحب المحفظة',
        max_length=100,
        help_text='الاسم كما هو مسجل في المحفظة'
    )
    is_active = models.BooleanField('نشط', default=True)
    created_at = models.DateTimeField('تاريخ الإنشاء', auto_now_add=True)
    
    class Meta:
        verbose_name = 'إعدادات المحفظة'
        verbose_name_plural = 'إعدادات المحفظة'
    
    def __str__(self):
        return f"{self.get_wallet_type_display()} - {self.wallet_number}"
    
    @classmethod
    def get_active_wallet(cls):
        """Get the active wallet configuration"""
        return cls.objects.filter(is_active=True).first()


class PaymentOrder(models.Model):
    """طلب الدفع"""
    
    STATUS_CHOICES = [
        ('pending', 'قيد الانتظار'),
        ('paid', 'تم الدفع ✅'),
        ('failed', 'فشل'),
        ('expired', 'منتهي'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('wallet', 'محفظة إلكترونية'),
        ('fawry', 'فوري'),
        ('code', 'كود تفعيل'),
    ]
    
    # رقم مرجعي بسيط للطالب
    reference_code = models.CharField(
        'الكود المرجعي',
        max_length=10,
        unique=True,
        editable=False,
        blank=True
    )
    
    # Relations
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='payment_orders',
        verbose_name='الطالب'
    )
    lecture = models.ForeignKey(
        'courses.Lecture',
        on_delete=models.CASCADE,
        related_name='payment_orders',
        verbose_name='المحاضرة'
    )
    
    # Payment details
    amount = models.DecimalField(
        'المبلغ (جنيه)',
        max_digits=8,
        decimal_places=2
    )
    payment_method = models.CharField(
        'طريقة الدفع',
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        default='wallet'
    )
    status = models.CharField(
        'الحالة',
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    
    # Student phone for verification
    student_phone = models.CharField(
        'رقم الطالب',
        max_length=15,
        blank=True
    )
    
    # Admin notes
    admin_notes = models.TextField(
        'ملاحظات الأدمن',
        blank=True,
        help_text='ملاحظات داخلية'
    )
    
    # Timestamps
    created_at = models.DateTimeField('تاريخ الإنشاء', auto_now_add=True)
    paid_at = models.DateTimeField('تاريخ الدفع', null=True, blank=True)
    
    class Meta:
        verbose_name = 'طلب دفع'
        verbose_name_plural = 'طلبات الدفع'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"#{self.reference_code} - {self.student.first_name} - {self.lecture.title}"
    
    def save(self, *args, **kwargs):
        # Generate reference code if not set
        if not self.reference_code:
            self.reference_code = self.generate_reference_code()
        
        # Auto-fill student phone
        if not self.student_phone and self.student:
            self.student_phone = self.student.phone_number
        
        super().save(*args, **kwargs)
    
    @staticmethod
    def generate_reference_code():
        """Generate a simple 6-digit reference code"""
        while True:
            code = ''.join(random.choices(string.digits, k=6))
            if not PaymentOrder.objects.filter(reference_code=code).exists():
                return code
