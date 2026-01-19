from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    path('', views.chapter_list, name='chapter_list'),
    path('chapter/<int:chapter_id>/', views.lecture_list, name='lecture_list'),
    path('lecture/<int:lecture_id>/', views.lecture_detail, name='lecture_detail'),
    path('lecture/<int:lecture_id>/progress/', views.update_progress, name='update_progress'),
]
