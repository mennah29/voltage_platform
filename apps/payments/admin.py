from django.contrib import admin
from django.utils import timezone
from .models import WalletConfig, PaymentOrder
from apps.courses.models import Enrollment


@admin.register(WalletConfig)
class WalletConfigAdmin(admin.ModelAdmin):
    """Admin for Wallet Configuration"""
    list_display = ['wallet_type', 'wallet_number', 'wallet_name', 'is_active']
    list_filter = ['wallet_type', 'is_active']
    
    fieldsets = (
        ('بيانات المحفظة', {
            'fields': ('wallet_type', 'wallet_number', 'wallet_name'),
            'description': 'أدخل بيانات محفظتك الإلكترونية - الطلاب هيحولوا عليها'
        }),
        ('الإعدادات', {
            'fields': ('is_active',),
        }),
    )


@admin.register(PaymentOrder)
class PaymentOrderAdmin(admin.ModelAdmin):
    """Admin for Payment Orders"""
    list_display = ['reference_code', 'student', 'student_phone', 'lecture', 'amount', 'status', 'created_at']
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['reference_code', 'student__first_name', 'student__phone_number', 'student_phone']
    readonly_fields = ['reference_code', 'student', 'lecture', 'amount', 'student_phone', 'created_at', 'paid_at']
    list_editable = ['status']  # Allow quick status change from list view
    
    fieldsets = (
        ('معلومات الطلب', {
            'fields': ('reference_code', 'student', 'student_phone', 'lecture', 'amount')
        }),
        ('تأكيد الدفع', {
            'fields': ('status', 'admin_notes'),
            'description': '⚠️ غيّر الحالة لـ "تم الدفع ✅" لتفعيل المحاضرة للطالب'
        }),
        ('التواريخ', {
            'fields': ('created_at', 'paid_at')
        }),
    )
    
    actions = ['mark_as_paid', 'mark_as_expired']
    
    def mark_as_paid(self, request, queryset):
        """Mark selected orders as paid and create enrollments"""
        count = 0
        for order in queryset.filter(status='pending'):
            order.status = 'paid'
            order.paid_at = timezone.now()
            order.save()
            
            # Create enrollment
            Enrollment.objects.get_or_create(
                student=order.student,
                lecture=order.lecture
            )
            count += 1
        
        self.message_user(request, f'تم تأكيد {count} طلب دفع وتفعيل المحاضرات ✅')
    mark_as_paid.short_description = '✅ تأكيد الدفع وتفعيل المحاضرة'
    
    def mark_as_expired(self, request, queryset):
        """Mark selected orders as expired"""
        count = queryset.filter(status='pending').update(status='expired')
        self.message_user(request, f'تم إلغاء {count} طلب')
    mark_as_expired.short_description = '❌ إلغاء الطلبات'
    
    def save_model(self, request, obj, form, change):
        """Auto-create enrollment when status changes to paid"""
        if change and obj.status == 'paid':
            if not obj.paid_at:
                obj.paid_at = timezone.now()
            
            # Create enrollment
            Enrollment.objects.get_or_create(
                student=obj.student,
                lecture=obj.lecture
            )
        
        super().save_model(request, obj, form, change)
