"""
URL configuration for Voltage Educational Platform.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('users/', include('apps.users.urls', namespace='users')),
    path('courses/', include('apps.courses.urls', namespace='courses')),
    path('exams/', include('apps.exams.urls', namespace='exams')),
    path('payments/', include('apps.payments.urls', namespace='payments')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
