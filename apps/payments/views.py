"""
Payment Views - Wallet Payment System
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import WalletConfig, PaymentOrder
from apps.courses.models import Lecture, Enrollment


@login_required
def initiate_payment(request, lecture_id):
    """Start payment for a lecture"""
    lecture = get_object_or_404(Lecture, id=lecture_id, is_active=True)
    
    # Check if already enrolled
    if Enrollment.objects.filter(student=request.user, lecture=lecture).exists():
        return redirect('courses:lecture_detail', lecture_id=lecture.id)
    
    # Check for existing pending order
    existing_order = PaymentOrder.objects.filter(
        student=request.user,
        lecture=lecture,
        status='pending'
    ).first()
    
    if existing_order:
        order = existing_order
    else:
        # Create new payment order
        order = PaymentOrder.objects.create(
            student=request.user,
            lecture=lecture,
            amount=lecture.price,
            payment_method='wallet'
        )
    
    # Get wallet config
    wallet = WalletConfig.get_active_wallet()
    
    context = {
        'lecture': lecture,
        'order': order,
        'wallet': wallet,
    }
    
    return render(request, 'payments/checkout.html', context)


@login_required
def payment_status(request, reference_code):
    """Check payment status"""
    order = get_object_or_404(PaymentOrder, reference_code=reference_code, student=request.user)
    
    # If paid, redirect to lecture
    if order.status == 'paid':
        messages.success(request, 'تم تأكيد الدفع! يمكنك مشاهدة المحاضرة الآن 🎉')
        return redirect('courses:lecture_detail', lecture_id=order.lecture.id)
    
    context = {
        'order': order,
        'lecture': order.lecture,
        'wallet': WalletConfig.get_active_wallet(),
    }
    return render(request, 'payments/status.html', context)


@login_required
def my_orders(request):
    """View user's payment orders"""
    orders = PaymentOrder.objects.filter(student=request.user)
    return render(request, 'payments/my_orders.html', {'orders': orders})
