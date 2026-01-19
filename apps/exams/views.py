from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from django.contrib import messages
import random
from .models import Quiz, Question, StudentResult


@login_required
def quiz_intro(request, quiz_id):
    """صفحة تعليمات الامتحان قبل البدء"""
    quiz = get_object_or_404(Quiz, id=quiz_id, is_active=True)
    
    # Check if user has access to the lecture
    from apps.courses.models import Enrollment
    enrollment = Enrollment.objects.filter(
        student=request.user,
        lecture=quiz.lecture
    ).first()
    
    if not enrollment and not quiz.lecture.is_free:
        messages.error(request, 'ليس لديك صلاحية الوصول لهذا الامتحان')
        return redirect('courses:lecture_list', chapter_id=quiz.lecture.chapter.id)
    
    # Check attempts
    attempts = StudentResult.objects.filter(
        student=request.user,
        quiz=quiz
    ).count()
    
    can_take = attempts < quiz.max_attempts
    
    context = {
        'quiz': quiz,
        'attempts': attempts,
        'can_take': can_take,
    }
    return render(request, 'exams/quiz_intro.html', context)


@login_required
def quiz_take(request, quiz_id):
    """صفحة حل الامتحان"""
    quiz = get_object_or_404(Quiz, id=quiz_id, is_active=True)
    
    # Check attempts
    attempts = StudentResult.objects.filter(
        student=request.user,
        quiz=quiz
    ).count()
    
    if attempts >= quiz.max_attempts:
        messages.error(request, 'لقد استنفذت جميع محاولاتك')
        return redirect('exams:quiz_intro', quiz_id=quiz.id)
    
    # Get questions
    questions = list(quiz.questions.all())
    if quiz.shuffle_questions:
        random.shuffle(questions)
    
    # Store start time in session
    request.session[f'quiz_{quiz.id}_start'] = timezone.now().isoformat()
    
    context = {
        'quiz': quiz,
        'questions': questions,
        'attempt_number': attempts + 1,
    }
    return render(request, 'exams/quiz_take.html', context)


@login_required
def quiz_submit(request, quiz_id):
    """تسليم الامتحان وحساب النتيجة"""
    if request.method != 'POST':
        return redirect('exams:quiz_take', quiz_id=quiz_id)
    
    quiz = get_object_or_404(Quiz, id=quiz_id)
    questions = quiz.questions.all()
    
    # Calculate time taken
    start_time_str = request.session.get(f'quiz_{quiz.id}_start')
    if start_time_str:
        from datetime import datetime
        start_time = datetime.fromisoformat(start_time_str)
        time_taken = int((timezone.now() - timezone.make_aware(start_time)).total_seconds())
    else:
        time_taken = 0
    
    # Grade the quiz
    correct_count = 0
    total_points = 0
    answers_data = {}
    
    for question in questions:
        answer = request.POST.get(f'question_{question.id}', '')
        is_correct = answer.lower() == question.correct_answer.lower()
        
        answers_data[str(question.id)] = {
            'answer': answer,
            'correct': question.correct_answer,
            'is_correct': is_correct
        }
        
        if is_correct:
            correct_count += 1
            total_points += question.points
    
    # Create result
    attempts = StudentResult.objects.filter(
        student=request.user,
        quiz=quiz
    ).count()
    
    result = StudentResult.objects.create(
        student=request.user,
        quiz=quiz,
        score=total_points,
        total_questions=questions.count(),
        correct_answers=correct_count,
        answers_data=answers_data,
        time_taken=time_taken,
        attempt_number=attempts + 1,
        completed_at=timezone.now()
    )
    
    # Calculate and save result
    result.calculate_result()
    result.save()
    
    # Clear session
    if f'quiz_{quiz.id}_start' in request.session:
        del request.session[f'quiz_{quiz.id}_start']
    
    return redirect('exams:quiz_result', result_id=result.id)


@login_required
def quiz_result(request, result_id):
    """صفحة عرض نتيجة الامتحان"""
    result = get_object_or_404(
        StudentResult,
        id=result_id,
        student=request.user
    )
    
    # Prepare questions with answers if allowed
    questions_with_answers = []
    if result.quiz.show_answers:
        for question in result.quiz.questions.all():
            q_data = result.answers_data.get(str(question.id), {})
            questions_with_answers.append({
                'question': question,
                'student_answer': q_data.get('answer', ''),
                'is_correct': q_data.get('is_correct', False),
            })
    
    context = {
        'result': result,
        'questions_with_answers': questions_with_answers,
    }
    return render(request, 'exams/result.html', context)


@login_required
def my_results(request):
    """صفحة كل نتائج الطالب"""
    results = StudentResult.objects.filter(
        student=request.user
    ).select_related('quiz', 'quiz__lecture')
    
    context = {
        'results': results
    }
    return render(request, 'exams/my_results.html', context)
