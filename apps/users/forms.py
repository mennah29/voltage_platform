from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User


class UserLoginForm(forms.Form):
    """نموذج تسجيل الدخول"""
    phone_number = forms.CharField(
        label='رقم الهاتف',
        max_length=11,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '01xxxxxxxxx',
            'dir': 'ltr'
        })
    )
    password = forms.CharField(
        label='كلمة السر',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '••••••••'
        })
    )


class UserRegisterForm(UserCreationForm):
    """نموذج تسجيل طالب جديد"""
    
    class Meta:
        model = User
        fields = [
            'phone_number',
            'first_name',
            'last_name',
            'parent_phone',
            'grade',
            'governorate',
            'password1',
            'password2'
        ]
        widgets = {
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '01xxxxxxxxx',
                'dir': 'ltr'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'الاسم الأول'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'اسم العائلة'
            }),
            'parent_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'رقم ولي الأمر',
                'dir': 'ltr'
            }),
            'grade': forms.Select(attrs={
                'class': 'form-select'
            }),
            'governorate': forms.Select(attrs={
                'class': 'form-select'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'كلمة السر'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'تأكيد كلمة السر'
        })
