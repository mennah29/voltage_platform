from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from .models import Chapter, Lecture, Enrollment


def chapter_list(request):
    """عرض قائمة الفصول حسب السنة الدراسية"""
    grade = request.GET.get('grade', None)
    
    # Validate grade - must be a valid number (1, 2, or 3)
    if grade and grade not in ['None', 'null', '']:
        try:
            grade = int(grade)
            if grade not in [1, 2, 3]:
                grade = None
        except (ValueError, TypeError):
            grade = None
    else:
        grade = None
    
    chapters = Chapter.objects.filter(is_active=True)
    if grade:
        chapters = chapters.filter(grade=grade)
    
    # Get user's enrolled lectures if authenticated
    enrolled_lectures = []
    if request.user.is_authenticated:
        enrolled_lectures = list(
            Enrollment.objects.filter(student=request.user)
            .values_list('lecture_id', flat=True)
        )
    
    context = {
        'chapters': chapters,
        'enrolled_lectures': enrolled_lectures,
        'selected_grade': grade,
    }
    return render(request, 'courses/chapter_list.html', context)


def lecture_list(request, chapter_id):
    """عرض محاضرات فصل معين"""
    chapter = get_object_or_404(Chapter, id=chapter_id, is_active=True)
    lectures = chapter.lectures.filter(is_active=True)
    
    # Get user's enrolled and completed lectures
    enrolled_ids = []
    completed_ids = []
    if request.user.is_authenticated:
        enrollments = Enrollment.objects.filter(
            student=request.user,
            lecture__chapter=chapter
        )
        enrolled_ids = list(enrollments.values_list('lecture_id', flat=True))
        completed_ids = list(
            enrollments.filter(is_completed=True)
            .values_list('lecture_id', flat=True)
        )
    
    context = {
        'chapter': chapter,
        'lectures': lectures,
        'enrolled_ids': enrolled_ids,
        'completed_ids': completed_ids,
    }
    return render(request, 'courses/lecture_list.html', context)


@login_required
def lecture_detail(request, lecture_id):
    """صفحة مشاهدة المحاضرة"""
    lecture = get_object_or_404(Lecture, id=lecture_id, is_active=True)
    
    # Check if user has access
    if not lecture.is_free:
        enrollment = Enrollment.objects.filter(
            student=request.user,
            lecture=lecture
        ).first()
        
        if not enrollment:
            # User doesn't have access
            return render(request, 'courses/access_denied.html', {
                'lecture': lecture
            })
    else:
        # Create enrollment for free lectures
        enrollment, _ = Enrollment.objects.get_or_create(
            student=request.user,
            lecture=lecture
        )
    
    # Check if there's a quiz for this lecture
    quiz = lecture.quizzes.first() if hasattr(lecture, 'quizzes') else None
    
    context = {
        'lecture': lecture,
        'enrollment': enrollment if not lecture.is_free else Enrollment.objects.filter(
            student=request.user, lecture=lecture
        ).first(),
        'quiz': quiz,
        # For watermark
        'student_phone': request.user.phone_number,
    }
    return render(request, 'courses/video_player.html', context)


@login_required
def update_progress(request, lecture_id):
    """تحديث نسبة مشاهدة الفيديو (AJAX)"""
    if request.method == 'POST':
        lecture = get_object_or_404(Lecture, id=lecture_id)
        progress = int(request.POST.get('progress', 0))
        
        enrollment = Enrollment.objects.filter(
            student=request.user,
            lecture=lecture
        ).first()
        
        if enrollment:
            enrollment.progress = min(progress, 100)
            if progress >= 90 and not enrollment.is_completed:
                enrollment.is_completed = True
                enrollment.completed_at = timezone.now()
                
                # Update user battery level
                request.user.battery_level = min(
                    request.user.battery_level + 5,
                    100
                )
                request.user.save()
            
            enrollment.save()
            
            return JsonResponse({
                'success': True,
                'progress': enrollment.progress,
                'completed': enrollment.is_completed
            })
    
    return JsonResponse({'success': False}, status=400)
