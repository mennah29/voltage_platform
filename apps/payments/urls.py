from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('pay/<int:lecture_id>/', views.initiate_payment, name='initiate_payment'),
    path('status/<str:reference_code>/', views.payment_status, name='payment_status'),
    path('my-orders/', views.my_orders, name='my_orders'),
]
