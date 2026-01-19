from django.urls import path
from . import views

app_name = 'exams'

urlpatterns = [
    path('quiz/<int:quiz_id>/', views.quiz_intro, name='quiz_intro'),
    path('quiz/<int:quiz_id>/take/', views.quiz_take, name='quiz_take'),
    path('quiz/<int:quiz_id>/submit/', views.quiz_submit, name='quiz_submit'),
    path('result/<int:result_id>/', views.quiz_result, name='quiz_result'),
    path('my-results/', views.my_results, name='my_results'),
]
