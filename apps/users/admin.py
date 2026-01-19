from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, ActivationCode


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin configuration for custom User model"""
    
    list_display = [
        'phone_number', 
        'first_name', 
        'last_name', 
        'role', 
        'grade', 
        'governorate',
        'battery_level',
        'is_active'
    ]
    
    list_filter = ['role', 'grade', 'governorate', 'is_active', 'created_at']
    
    search_fields = ['phone_number', 'first_name', 'last_name', 'parent_phone']
    
    ordering = ['-created_at']
    
    fieldsets = (
        ('بيانات الدخول', {
            'fields': ('phone_number', 'password')
        }),
        ('البيانات الشخصية', {
            'fields': ('first_name', 'last_name', 'profile_pic')
        }),
        ('بيانات الطالب', {
            'fields': ('parent_phone', 'grade', 'governorate', 'battery_level')
        }),
        ('الصلاحيات', {
            'fields': ('role', 'is_active', 'is_staff', 'is_superuser'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        ('بيانات المستخدم الجديد', {
            'classes': ('wide',),
            'fields': (
                'phone_number', 
                'first_name', 
                'last_name',
                'password1', 
                'password2',
                'role',
                'grade',
                'governorate',
                'parent_phone'
            ),
        }),
    )


@admin.register(ActivationCode)
class ActivationCodeAdmin(admin.ModelAdmin):
    """Admin for activation codes"""
    
    list_display = ['code', 'lecture', 'is_used', 'used_by', 'created_at', 'used_at']
    list_filter = ['is_used', 'lecture__chapter', 'created_at']
    search_fields = ['code', 'used_by__phone_number']
    readonly_fields = ['used_at']
    
    actions = ['generate_codes']
    
    def generate_codes(self, request, queryset):
        """Action to generate multiple codes"""
        # This will be implemented with a custom view
        pass
    generate_codes.short_description = "توليد أكواد جديدة"
