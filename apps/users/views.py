from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import User, ActivationCode
from .forms import UserLoginForm, UserRegisterForm


def login_view(request):
    """تسجيل الدخول برقم الهاتف"""
    if request.user.is_authenticated:
        # لو أدمن يروح لصفحة الإدارة
        if request.user.is_staff:
            return redirect('/admin/')
        return redirect('users:dashboard')
    
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            phone_number = form.cleaned_data['phone_number']
            password = form.cleaned_data['password']
            user = authenticate(request, username=phone_number, password=password)
            
            if user is not None:
                login(request, user)
                # لو أدمن يروح لصفحة الإدارة
                if user.is_staff:
                    messages.success(request, f'أهلاً بك {user.first_name}! 🔧 تم توجيهك لصفحة الإدارة')
                    return redirect('/admin/')
                messages.success(request, f'أهلاً بك {user.first_name}! ⚡')
                return redirect('users:dashboard')
            else:
                messages.error(request, 'رقم الهاتف أو كلمة السر غير صحيحة')
    else:
        form = UserLoginForm()
    
    return render(request, 'users/login.html', {'form': form})


def logout_view(request):
    """تسجيل الخروج"""
    logout(request)
    messages.info(request, 'تم تسجيل الخروج بنجاح')
    return redirect('home')


def register_view(request):
    """تسجيل طالب جديد"""
    if request.user.is_authenticated:
        return redirect('users:dashboard')
    
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'تم إنشاء حسابك بنجاح! أهلاً بك في Voltage ⚡')
            return redirect('users:dashboard')
    else:
        form = UserRegisterForm()
    
    return render(request, 'users/register.html', {'form': form})


@login_required
def dashboard_view(request):
    """لوحة تحكم الطالب"""
    # Get user's enrolled lectures
    from apps.courses.models import Enrollment
    
    enrollments = Enrollment.objects.filter(student=request.user).select_related('lecture', 'lecture__chapter')
    
    context = {
        'enrollments': enrollments,
        'battery_level': request.user.battery_level,
    }
    return render(request, 'users/dashboard.html', context)


@login_required
def activate_code_view(request):
    """تفعيل كود محاضرة"""
    if request.method == 'POST':
        code_value = request.POST.get('code', '').strip().upper()
        
        try:
            code = ActivationCode.objects.get(code=code_value, is_used=False)
            
            # Activate the code
            code.is_used = True
            code.used_by = request.user
            code.used_at = timezone.now()
            code.save()
            
            # Create enrollment
            from apps.courses.models import Enrollment
            Enrollment.objects.get_or_create(
                student=request.user,
                lecture=code.lecture
            )
            
            messages.success(request, f'تم تفعيل المحاضرة: {code.lecture.title} ⚡')
            
        except ActivationCode.DoesNotExist:
            messages.error(request, 'الكود غير صحيح أو مستخدم من قبل')
        
        return redirect('users:dashboard')
    
    return render(request, 'users/activate_code.html')


@login_required
def profile_view(request):
    """صفحة الملف الشخصي"""
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.parent_phone = request.POST.get('parent_phone', user.parent_phone)
        user.governorate = request.POST.get('governorate', user.governorate)
        
        if 'profile_pic' in request.FILES:
            user.profile_pic = request.FILES['profile_pic']
        
        user.save()
        messages.success(request, 'تم تحديث بياناتك بنجاح')
        return redirect('users:profile')
    
    return render(request, 'users/profile.html')
